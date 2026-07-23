import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from db.models import PromptLog
from db.repositories import get_session, save_prompt_log, update_session
from engine.evaluators.regex_matcher import check_exact_match
from engine.evaluators.tool_verifier import check_tool_call
from engine.llm_router import route_prompt
from engine.prompts.level_1_lobby import LEVEL_1_SECRET_TAG, LEVEL_1_SYSTEM_PROMPT
from engine.prompts.level_2_lab import LEVEL_2_SYSTEM_PROMPT
from engine.tools import LEVEL_2_TOOLS
from schemas.payload import PromptSubmissionRequest
from schemas.response import PromptSubmissionResponse

router = APIRouter(prefix="/api/v1/game", tags=["Game Engine"])

# Level 3 isn't wired in here yet - the AI Judge evaluator is a Week 7-8 item.
_LEVEL_PROMPTS = {
    1: (LEVEL_1_SYSTEM_PROMPT, None),
    2: (LEVEL_2_SYSTEM_PROMPT, LEVEL_2_TOOLS),
}


@router.post("/submit-prompt", response_model=PromptSubmissionResponse)
async def submit_prompt(payload: PromptSubmissionRequest):
    session = get_session(payload.session_token)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.is_game_over:
        raise HTTPException(status_code=400, detail="This session has already ended.")

    if datetime.now(timezone.utc) >= session.expires_at:
        update_session(session.session_token, is_game_over=True)
        return _build_response(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            ai_response="",
            is_win=False,
            win_reason="Time limit exceeded.",
            session=session,
            latency_ms=0,
        )

    system_prompt, tools = _LEVEL_PROMPTS.get(payload.level_id, (None, None))
    if system_prompt is None:
        raise HTTPException(status_code=400, detail=f"Level {payload.level_id} is not playable yet.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": payload.user_prompt},
    ]

    start = time.perf_counter()
    completion = await route_prompt(payload.level_id, messages, tools=tools)
    latency_ms = int((time.perf_counter() - start) * 1000)

    ai_message = completion.choices[0].message
    ai_response_text = ai_message.content or ""

    if payload.level_id == 1:
        is_win, win_reason = check_exact_match(ai_response_text, LEVEL_1_SECRET_TAG)
    else:
        is_win, win_reason = check_tool_call(completion, tool_name="open_vault")

    attempts_used = session.attempts_used + 1
    is_game_over = is_win or attempts_used >= session.max_attempts
    session = update_session(session.session_token, attempts_used=attempts_used, is_game_over=is_game_over)

    message_id = f"msg_{uuid.uuid4().hex[:8]}"
    save_prompt_log(
        PromptLog(
            message_id=message_id,
            session_token=session.session_token,
            level_id=payload.level_id,
            user_prompt=payload.user_prompt,
            ai_response=ai_response_text,
            is_win=is_win,
            win_reason=win_reason,
            latency_ms=latency_ms,
        )
    )

    return _build_response(
        message_id=message_id,
        ai_response=ai_response_text,
        is_win=is_win,
        win_reason=win_reason,
        session=session,
        latency_ms=latency_ms,
    )


def _build_response(*, message_id, ai_response, is_win, win_reason, session, latency_ms):
    time_remaining = max(0, int((session.expires_at - datetime.now(timezone.utc)).total_seconds()))
    return {
        "status": "success",
        "data": {
            "message_id": message_id,
            "ai_response": ai_response,
            "verification": {
                "is_win": is_win,
                "win_reason": win_reason,
                "metadata": None,
            },
            "session_state": {
                "attempts_used": session.attempts_used,
                "attempts_left": max(0, session.max_attempts - session.attempts_used),
                "time_remaining_seconds": time_remaining,
                "is_game_over": session.is_game_over,
            },
            "performance": {"latency_ms": latency_ms},
        },
    }
