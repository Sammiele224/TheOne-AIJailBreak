"""Repository functions for database access."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db.models import LevelConfig, PlayerSession, PromptLog, VerificationResult


def _rollback_and_raise(db: Session, exc: SQLAlchemyError) -> None:
	"""Rollback the active transaction and re-raise the original exception."""

	db.rollback()
	raise exc


def create_session(
	db: Session,
	*,
	session_token: str,
	level_id: uuid.UUID,
	attempts_used: int,
	max_attempts: int,
	expires_at: datetime,
	started_at: datetime | None = None,
	completed: bool = False,
) -> PlayerSession:
	"""Create and persist a new player session."""

	session = PlayerSession(
		session_token=session_token,
		level_id=level_id,
		attempts_used=attempts_used,
		max_attempts=max_attempts,
		expires_at=expires_at,
		started_at=started_at if started_at is not None else datetime.now(timezone.utc),
		completed=completed,
	)

	try:
		db.add(session)
		db.commit()
		db.refresh(session)
		return session
	except SQLAlchemyError as exc:
		_rollback_and_raise(db, exc)


def get_session_by_token(db: Session, session_token: str) -> PlayerSession | None:
	"""Return a player session by its token."""

	try:
		statement = select(PlayerSession).where(PlayerSession.session_token == session_token)
		return db.execute(statement).scalar_one_or_none()
	except SQLAlchemyError as exc:
		_rollback_and_raise(db, exc)


def update_attempts(db: Session, session_token: str, attempts_used: int) -> PlayerSession | None:
	"""Update the attempts used for a player session."""

	try:
		session = get_session_by_token(db, session_token)
		if session is None:
			return None

		session.attempts_used = attempts_used
		db.commit()
		db.refresh(session)
		return session
	except SQLAlchemyError as exc:
		_rollback_and_raise(db, exc)


def mark_completed(db: Session, session_token: str, completed: bool = True) -> PlayerSession | None:
	"""Mark a player session as completed or not completed."""

	try:
		session = get_session_by_token(db, session_token)
		if session is None:
			return None

		session.completed = completed
		db.commit()
		db.refresh(session)
		return session
	except SQLAlchemyError as exc:
		_rollback_and_raise(db, exc)


def create_prompt_log(
	db: Session,
	*,
	session_id: uuid.UUID,
	user_prompt: str,
	model_response: str,
	passed: bool,
	latency_ms: int,
) -> PromptLog:
	"""Create and persist a prompt log record."""

	prompt_log = PromptLog(
		session_id=session_id,
		user_prompt=user_prompt,
		model_response=model_response,
		passed=passed,
		latency_ms=latency_ms,
	)

	try:
		db.add(prompt_log)
		db.commit()
		db.refresh(prompt_log)
		return prompt_log
	except SQLAlchemyError as exc:
		_rollback_and_raise(db, exc)


def get_logs_by_session(db: Session, session_id: uuid.UUID) -> list[PromptLog]:
	"""Return all prompt logs for a player session."""

	try:
		statement = select(PromptLog).where(PromptLog.session_id == session_id).order_by(PromptLog.created_at.asc())
		return list(db.execute(statement).scalars().all())
	except SQLAlchemyError as exc:
		_rollback_and_raise(db, exc)


def get_level_config(db: Session, level_id: uuid.UUID) -> LevelConfig | None:
	"""Return a level configuration by its identifier."""

	try:
		statement = select(LevelConfig).where(LevelConfig.id == level_id)
		return db.execute(statement).scalar_one_or_none()
	except SQLAlchemyError as exc:
		_rollback_and_raise(db, exc)


def get_level_config_by_number(db: Session, level_number: int) -> LevelConfig | None:
	"""Return a level configuration by its gameplay number."""

	try:
		statement = select(LevelConfig).where(LevelConfig.level_number == level_number)
		return db.execute(statement).scalar_one_or_none()
	except SQLAlchemyError as exc:
		_rollback_and_raise(db, exc)


def create_result(
	db: Session,
	*,
	prompt_log_id: uuid.UUID,
	passed: bool,
	reason: str,
	evaluator_type: str,
) -> VerificationResult:
	"""Create and persist a verification result record."""

	result = VerificationResult(
		prompt_log_id=prompt_log_id,
		passed=passed,
		reason=reason,
		evaluator_type=evaluator_type,
	)

	try:
		db.add(result)
		db.commit()
		db.refresh(result)
		return result
	except SQLAlchemyError as exc:
		_rollback_and_raise(db, exc)