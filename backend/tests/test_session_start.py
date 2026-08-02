from datetime import datetime, timedelta, timezone

from db.models import LevelConfig, PlayerSession
from db.repositories import create_session


def test_create_session_persists_basic_state(session_db):
    level = LevelConfig(
        level_number=1,
        level_name="The Lobby",
        model_provider="groq",
        model_name="gemma2-2b-it",
        system_prompt="prompt",
        max_attempts=3,
        timeout_seconds=60,
    )
    session_db.add(level)
    session_db.commit()
    session_db.refresh(level)

    created = create_session(
        session_db,
        session_token="token-123",
        level_id=level.id,
        attempts_used=0,
        max_attempts=3,
        started_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        completed=False,
    )

    assert isinstance(created, PlayerSession)
    assert created.session_token == "token-123"
