"""Database engine and session management for SQLAlchemy 2.0."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings
from db.models import Base


DATABASE_URL = settings.database_url or "sqlite:///./neurocorp_dev.db"
metadata = Base.metadata

engine_kwargs: dict[str, object] = {
	"future": True,
}

if DATABASE_URL.startswith("sqlite"):
	engine_kwargs.update(
		{
			"connect_args": {"check_same_thread": False},
		}
	)
else:
	engine_kwargs.update(
		{
			"pool_pre_ping": True,
			"pool_recycle": 1800,
			"pool_size": 5,
			"max_overflow": 10,
			"pool_timeout": 30,
		}
	)

engine: Engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
	bind=engine,
	autoflush=False,
	autocommit=False,
	expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
	"""Yield a database session and ensure it is closed after use."""

	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

