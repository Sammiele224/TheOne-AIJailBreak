from datetime import datetime, timezone

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PlayerSession(BaseModel):
    session_token: str
    current_level: int = 1
    attempts_used: int = 0
    max_attempts: int = 20
    is_game_over: bool = False
    created_at: datetime = Field(default_factory=_utcnow)
    expires_at: datetime


class PromptLog(BaseModel):
    message_id: str
    session_token: str
    level_id: int
    user_prompt: str
    ai_response: str
    is_win: bool
    win_reason: str
    latency_ms: int
    created_at: datetime = Field(default_factory=_utcnow)


class LevelConfig(BaseModel):
    level_id: int
    name: str
    system_prompt: str
    max_attempts: int = 20
    time_limit_seconds: int = 900
    secret_tag: str | None = None
    tools: list[dict] | None = None


class VerificationResult(BaseModel):
    is_win: bool
    win_reason: str
    metadata: dict | None = None
