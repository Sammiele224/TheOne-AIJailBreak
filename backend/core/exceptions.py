"""Custom exception types for the game backend."""

from __future__ import annotations


class GameError(Exception):
    """Base exception for game-specific failures."""


class SessionExpiredError(GameError):
    """Raised when a session has expired."""


class InvalidSessionError(GameError):
    """Raised when a session token is invalid."""
