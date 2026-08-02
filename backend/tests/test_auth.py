from starlette.requests import Request

from core import auth


def test_allows_requests_when_no_api_key_is_configured(monkeypatch):
    monkeypatch.setattr(auth.settings, "api_key", None)
    monkeypatch.setattr(auth.settings, "debug", False)

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/game/start-game",
            "headers": [],
            "query_string": b"",
        }
    )

    assert auth.is_request_authorized(request) is True
