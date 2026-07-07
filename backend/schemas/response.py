from pydantic import BaseModel
from typing import Optional, Any, Dict

class VerificationData(BaseModel):
    is_win: bool
    win_reason: str
    metadata: Optional[Dict[str, Any]] = None

class SessionState(BaseModel):
    attempts_used: int
    attempts_left: int
    time_remaining_seconds: int
    is_game_over: bool

class PerformanceMetrics(BaseModel):
    latency_ms: int

class GameResponseData(BaseModel):
    message_id: str
    ai_response: str
    verification: VerificationData
    session_state: SessionState
    performance: PerformanceMetrics

class PromptSubmissionResponse(BaseModel):
    status: str = "success"
    data: GameResponseData