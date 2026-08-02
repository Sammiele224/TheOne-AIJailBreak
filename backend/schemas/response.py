from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class VerificationData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_win: bool
    win_reason: str
    metadata: dict[str, Any] | None = None


class SessionState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempts_used: int
    attempts_left: int
    time_remaining_seconds: int
    is_game_over: bool


class PerformanceMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latency_ms: int


class GameResponseData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_id: str
    ai_response: str
    verification: VerificationData
    session_state: SessionState
    performance: PerformanceMetrics


class PromptSubmissionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "success"
    data: GameResponseData