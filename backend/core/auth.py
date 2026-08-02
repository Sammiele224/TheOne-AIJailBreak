"""Authentication helpers for optional API-key protection."""

from __future__ import annotations

from fastapi import Request

from core.config import settings


PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


def get_request_api_key(request: Request) -> str | None:
    """Return an API key from the request headers if present."""

    return request.headers.get("X-API-Key") or request.headers.get("x-api-key")


def is_request_authorized(request: Request) -> bool:
    """Allow health probes and local development traffic when no API key is configured."""

    if request.url.path in PUBLIC_PATHS:
        return True

    configured_key = (settings.api_key or "").strip()
    if not configured_key:
        return True

    provided_key = (get_request_api_key(request) or "").strip()
    return bool(provided_key and provided_key == configured_key)
