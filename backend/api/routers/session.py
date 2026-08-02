"""Session management endpoints for game startup."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.dependencies import get_db
from db.models import LevelConfig
from db.repositories import create_session, get_level_config_by_number


router = APIRouter(prefix="/api/v1/game", tags=["Game Sessions"])


class StartGameRequest(BaseModel):
    """Payload used to create a new game session."""

    level_id: int = Field(..., ge=1, le=3)


class StartGameResponse(BaseModel):
    """Response payload returned after a game session is created."""

    session_token: str
    expires_at: datetime
    max_attempts: int


def _resolve_level_config(db: Session, level_id: int) -> LevelConfig:
    """Resolve a level configuration by gameplay level number."""

    level_config = get_level_config_by_number(db, level_id)

    if level_config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level {level_id} is not configured.",
        )

    return level_config


@router.post("/start-game", response_model=StartGameResponse, status_code=status.HTTP_201_CREATED)
def start_game(
    payload: StartGameRequest,
    db: Session = Depends(get_db),
) -> StartGameResponse:
    """Start a new game session and persist it to the database."""

    try:
        level_config = _resolve_level_config(db, payload.level_id)
        now = datetime.now(timezone.utc)
        session_token = str(uuid.uuid4())
        expires_at = now + timedelta(minutes=15)

        session = create_session(
            db,
            session_token=session_token,
            level_id=level_config.id,
            attempts_used=0,
            max_attempts=level_config.max_attempts,
            started_at=now,
            expires_at=expires_at,
            completed=False,
        )

        # SQLite drops tzinfo on round-trip, so re-attach UTC before serializing.
        # Without an offset, clients parse the timestamp as local time and treat
        # the session as already expired.
        stored_expires_at = session.expires_at
        if stored_expires_at.tzinfo is None:
            stored_expires_at = stored_expires_at.replace(tzinfo=timezone.utc)

        return StartGameResponse(
            session_token=session.session_token,
            expires_at=stored_expires_at,
            max_attempts=session.max_attempts,
        )
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while starting the game session.",
        ) from exc