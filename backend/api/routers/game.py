from fastapi import APIRouter, HTTPException, status
from schemas.payload import PromptSubmissionRequest
from schemas.response import PromptSubmissionResponse

router = APIRouter(prefix="/api/v1/game", tags=["Game Engine"])

@router.post("/submit-prompt", response_model=PromptSubmissionResponse)
async def submit_prompt(payload: PromptSubmissionRequest):
    # TODO: Connect llm_router.py and evaluators here later!
    
    # Example dummy response matching your contract:
    return {
        "status": "success",
        "data": {
            "message_id": "msg_9901",
            "ai_response": "Quyền truy cập bị từ chối. [ACCESS_GRANTED]",
            "verification": {
                "is_win": True,
                "win_reason": "Exact match keyword [ACCESS_GRANTED] detected.",
                "metadata": None
            },
            "session_state": {
                "attempts_used": payload.attempt_counter,
                "attempts_left": 20 - payload.attempt_counter,
                "time_remaining_seconds": 680,
                "is_game_over": False
            },
            "performance": {
                "latency_ms": 1420
            }
        }
    }