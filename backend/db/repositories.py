import uuid
from datetime import datetime, timedelta, timezone

from db.models import PlayerSession, PromptLog

# In-memory stand-in for the real Supabase/Postgres tables until db/client.py
# exists (blocked on My An's connection string). Function names/signatures
# match what the real-DB-backed version will need, so callers won't change
# when the storage backend does.
SESSIONS: dict[str, PlayerSession] = {}
PROMPT_LOGS: list[PromptLog] = []


def create_session(level_id: int = 1, max_attempts: int = 20, time_limit_seconds: int = 900) -> PlayerSession:
    session = PlayerSession(
        session_token=f"neuro_sec_{uuid.uuid4().hex[:12]}",
        current_level=level_id,
        max_attempts=max_attempts,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=time_limit_seconds),
    )
    SESSIONS[session.session_token] = session
    return session


def get_session(session_token: str) -> PlayerSession | None:
    return SESSIONS.get(session_token)


def update_session(session_token: str, **fields) -> PlayerSession:
    session = SESSIONS[session_token]
    for key, value in fields.items():
        setattr(session, key, value)
    return session


def save_prompt_log(log: PromptLog) -> None:
    PROMPT_LOGS.append(log)


def get_prompt_logs(session_token: str) -> list[PromptLog]:
    return [log for log in PROMPT_LOGS if log.session_token == session_token]
