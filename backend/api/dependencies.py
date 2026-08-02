"""FastAPI dependency providers for the API layer."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from db.client import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
	"""Yield a database session for request handlers."""

	yield from _get_db()