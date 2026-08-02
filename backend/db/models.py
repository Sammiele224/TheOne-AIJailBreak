"""SQLAlchemy declarative models for the game backend."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
	"""Base class for all database models."""


class PlayerSession(Base):
	"""Represents a player's run through a level."""

	__tablename__ = "player_sessions"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)
	session_token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
	level_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("level_configs.id", ondelete="RESTRICT"),
		index=True,
		nullable=False,
	)
	attempts_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	max_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
	started_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		nullable=False,
		server_default=func.now(),
	)
	expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		nullable=False,
		server_default=func.now(),
	)

	level: Mapped["LevelConfig"] = relationship(back_populates="sessions")
	prompt_logs: Mapped[list[PromptLog]] = relationship(
		back_populates="session",
		cascade="all, delete-orphan",
		passive_deletes=True,
	)


class LevelConfig(Base):
	"""Stores the configuration for a game level."""

	__tablename__ = "level_configs"
	__table_args__ = (Index("ix_level_configs_level_number", "level_number", unique=True),)

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)
	level_number: Mapped[int] = mapped_column(Integer, nullable=False)
	level_name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
	model_provider: Mapped[str] = mapped_column(String(50), nullable=False)
	model_name: Mapped[str] = mapped_column(String(120), nullable=False)
	system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
	max_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
	timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		nullable=False,
		server_default=func.now(),
	)

	sessions: Mapped[list["PlayerSession"]] = relationship(back_populates="level")


class PromptLog(Base):
	"""Stores a user prompt and the corresponding model response."""

	__tablename__ = "prompt_logs"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)
	session_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("player_sessions.id", ondelete="CASCADE"),
		nullable=False,
		index=True,
	)
	user_prompt: Mapped[str] = mapped_column(Text, nullable=False)
	model_response: Mapped[str] = mapped_column(Text, nullable=False)
	passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		nullable=False,
		server_default=func.now(),
	)

	session: Mapped["PlayerSession"] = relationship(back_populates="prompt_logs")
	verification_result: Mapped[Optional["VerificationResult"]] = relationship(
		back_populates="prompt_log",
		cascade="all, delete-orphan",
		uselist=False,
		passive_deletes=True,
	)


class VerificationResult(Base):
	"""Stores the outcome of prompt verification."""

	__tablename__ = "verification_results"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
	)
	prompt_log_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("prompt_logs.id", ondelete="CASCADE"),
		unique=True,
		nullable=False,
		index=True,
	)
	passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
	reason: Mapped[str] = mapped_column(Text, nullable=False)
	evaluator_type: Mapped[str] = mapped_column(String(80), nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		nullable=False,
		server_default=func.now(),
	)

	prompt_log: Mapped["PromptLog"] = relationship(back_populates="verification_result")

