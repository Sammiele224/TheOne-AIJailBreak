"""Game submission endpoints."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_db
from core.exceptions import GameError, InvalidSessionError, SessionExpiredError
from core.logging import get_logger, log_event
from db.models import LevelConfig, PlayerSession, PromptLog, VerificationResult
from engine.evaluators.llm_judge import LLMJudge
from engine.evaluators.regex_matcher import RegexEvaluator
from engine.evaluators.tool_verifier import ToolVerifier
from engine.llm_router import LLMRouter
from engine.tools import OPEN_VAULT_TOOL
from schemas.payload import PromptSubmissionRequest
from schemas.response import PromptSubmissionResponse


router = APIRouter(prefix="/api/v1/game", tags=["Game Engine"])
logger = get_logger("neurocorp.game_router")

class SessionStatusResponse(BaseModel):
    """Current server-side state of a player session."""

    session_token: str
    level_id: int
    level_name: str
    attempts_used: int
    max_attempts: int
    attempts_left: int
    completed: bool
    expired: bool
    is_game_over: bool
    expires_at: datetime


class SubmitPromptResponse(BaseModel):
    """Response returned after a prompt is evaluated."""

    model_response: str
    passed: bool
    reason: str
    attempts_left: int
    session_status: SessionStatusResponse


def _resolve_level_config_by_position(db: Session, level_id: int) -> LevelConfig:
    """Resolve a level config by gameplay level number."""

    statement = select(LevelConfig).where(LevelConfig.level_number == level_id)
    level_config = db.execute(statement).scalar_one_or_none()

    if level_config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level {level_id} is not configured.",
        )

    return level_config


def _serialize_raw_response(raw_response: Any) -> str:
    """Convert a provider response into a storable string."""

    if isinstance(raw_response, dict):
        return json.dumps(raw_response, ensure_ascii=False, default=str)

    model_dump = getattr(raw_response, "model_dump", None)
    if callable(model_dump):
        return json.dumps(model_dump(), ensure_ascii=False, default=str)

    return str(raw_response)


def _build_messages(system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
    """Build chat messages for the LLM provider."""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


async def _evaluate_response(
    *,
    level_number: int,
    system_prompt: str,
    user_prompt: str,
    model_response: str,
    raw_response: Any,
    router_client: LLMRouter,
) -> dict[str, bool | str]:
    """Run the level-specific evaluator."""

    if level_number == 1:
        return RegexEvaluator(system_prompt=system_prompt, model_response=model_response).evaluate()

    if level_number == 2:
        return ToolVerifier(response=raw_response, content_fallback=model_response).evaluate()

    if level_number == 3:
        # The guardian never grades itself: a second model reviews its reply.
        judge_result = await router_client.call_judge(
            user_prompt=user_prompt,
            guardian_response=model_response,
        )
        return LLMJudge(response=judge_result).evaluate()

    return {
        "passed": False,
        "reason": f"Unsupported level_id: {level_number}",
    }


@router.post("/submit-prompt", response_model=PromptSubmissionResponse)
async def submit_prompt(
    payload: PromptSubmissionRequest,
    db: Session = Depends(get_db),
) -> PromptSubmissionResponse:
    """Submit a prompt, call the appropriate model, and persist the result."""

    try:
        started_at = perf_counter()
        session = (
            db.execute(
                select(PlayerSession).where(PlayerSession.session_token == payload.session_token)
            )
            .scalar_one_or_none()
        )
        if session is None:
            raise InvalidSessionError("Invalid session token.")

        now = datetime.now(timezone.utc)
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= now:
            raise SessionExpiredError("Session has expired.")

        if session.completed:
            raise GameError("Session has already been completed.")

        if session.attempts_used >= session.max_attempts:
            raise GameError("No attempts remaining for this session.")

        active_level = db.execute(select(LevelConfig).where(LevelConfig.id == session.level_id)).scalar_one_or_none()
        if active_level is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Session references an unknown level configuration.",
            )

        if active_level.level_number != payload.level_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payload level_id does not match the active session level.",
            )

        messages = _build_messages(active_level.system_prompt, payload.user_prompt)
        router_client = LLMRouter()
        tools = [OPEN_VAULT_TOOL] if active_level.level_number == 2 else None
        llm_result = await router_client.call_model(
            payload.level_id,
            messages,
            tools=tools,
        )

        model_response_text = llm_result.get("content") or ""
        if not model_response_text.strip():
            model_response_text = _serialize_raw_response(llm_result.get("raw"))

        evaluation = await _evaluate_response(
            level_number=active_level.level_number,
            system_prompt=active_level.system_prompt,
            user_prompt=payload.user_prompt,
            model_response=model_response_text,
            raw_response=llm_result.get("raw"),
            router_client=router_client,
        )

        expected_attempt_counter = session.attempts_used + 1
        if payload.attempt_counter != expected_attempt_counter:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attempt counter does not match the server session state.",
            )

        next_attempts_used = expected_attempt_counter
        attempts_left = max(active_level.max_attempts - next_attempts_used, 0)
        is_game_over = bool(evaluation["passed"]) or next_attempts_used >= active_level.max_attempts
        latency_ms = int((perf_counter() - started_at) * 1000)

        prompt_log = PromptLog(
            session_id=session.id,
            user_prompt=payload.user_prompt,
            model_response=model_response_text,
            passed=bool(evaluation["passed"]),
            latency_ms=latency_ms,
        )
        verification_result = VerificationResult(
            prompt_log=prompt_log,
            passed=bool(evaluation["passed"]),
            reason=str(evaluation["reason"]),
            evaluator_type=(
                "regex" if payload.level_id == 1 else "tool" if payload.level_id == 2 else "unknown"
            ),
        )

        session.attempts_used = next_attempts_used
        session.completed = bool(evaluation["passed"]) or attempts_left == 0

        db.add(prompt_log)
        db.add(verification_result)
        db.flush()
        db.commit()
        db.refresh(session)
        db.refresh(prompt_log)
        db.refresh(verification_result)

        log_event(
            logger,
            event="prompt_submitted",
            session_token=payload.session_token,
            level_id=payload.level_id,
            attempts=payload.attempt_counter,
        )

        return PromptSubmissionResponse(
            status="success",
            data={
                "message_id": str(prompt_log.id),
                "ai_response": model_response_text,
                "verification": {
                    "is_win": bool(evaluation["passed"]),
                    "win_reason": str(evaluation["reason"]),
                    "metadata": {
                        "level_name": active_level.level_name,
                        "provider": active_level.model_provider,
                        "latency_ms": latency_ms,
                    },
                },
                "session_state": {
                    "attempts_used": session.attempts_used,
                    "attempts_left": attempts_left,
                    "time_remaining_seconds": max(int((expires_at - datetime.now(timezone.utc)).total_seconds()), 0),
                    "is_game_over": is_game_over,
                },
                "performance": {"latency_ms": latency_ms},
            },
        )
    except HTTPException:
        raise
    except InvalidSessionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SessionExpiredError as exc:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(exc)) from exc
    except GameError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception as exc:
        db.rollback()
        log_event(logger, event="prompt_submit_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while processing the prompt.",
        ) from exc
