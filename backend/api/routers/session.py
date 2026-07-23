from datetime import datetime, timezone

from fastapi import APIRouter

from db.repositories import create_session
from schemas.payload import StartGameRequest
from schemas.response import StartGameResponse

router = APIRouter(prefix="/api/v1/game", tags=["Game Engine"])


@router.post("/start-game", response_model=StartGameResponse)
async def start_game(payload: StartGameRequest):
    session = create_session(level_id=payload.level_id)
    time_remaining = int((session.expires_at - datetime.now(timezone.utc)).total_seconds())

    return {
        "status": "success",
        "data": {
            "session_token": session.session_token,
            "level_id": session.current_level,
            "session_state": {
                "attempts_used": session.attempts_used,
                "attempts_left": session.max_attempts - session.attempts_used,
                "time_remaining_seconds": time_remaining,
                "is_game_over": session.is_game_over,
            },
        },
    }
