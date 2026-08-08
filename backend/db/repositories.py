import os 
from typing import Optional
from backend.db.models import PlayerSession, PromptLog
from backend.db.client import get_pool

USE_IN_MEMORY = os.getenv("USE_IN_MEMORY_DB", "0") == "1" or not os.getenv("DATABASE_URL")

#MEMORY STORE
_sessions_db = {}
_prompt_logs_db = []

async def create_session(level_id: int, max_attempts: int, time_limit_seconds: int) -> PlayerSession:
    session = PlayerSession(...)

    if USE_IN_MEMORY:
        _sessions_db[session.session_token] = session
        return session

    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO player_sessions (session_token, current_level, attempts_used, max_attempts, is_game_over, created_at, expires_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
            session.session_token, session.current_level, session.attempts_used,
            session.max_attempts, session.is_game_over, session.created_at, session.expires_at
        )
    return session

async def get_session(session_token: str) -> Optional[PlayerSession]:
    if USE_IN_MEMORY:
        return _sessions_db.get(session_token)

    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM player_sessions WHERE session_token = $1", session_token)
        if not row:
            return None
        return PlayerSession(**dict(row))

# Tương tự chuyển update_session, save_prompt_log, get_prompt_logs sang async def với SQL query
