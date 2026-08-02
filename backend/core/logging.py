"""Structured logging helpers for the FastAPI backend."""

from __future__ import annotations

import logging
import sys
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with structured JSON-like formatting."""

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def log_event(logger: logging.Logger, *, event: str, **context: Any) -> None:
    """Emit a simple structured log entry using key/value context."""

    payload = [event]
    for key, value in context.items():
        payload.append(f"{key}={value}")
    logger.info(" | ".join(payload))
