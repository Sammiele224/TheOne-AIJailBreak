# API Documentation

## Health

- `GET /health` returns a health payload for orchestration systems.
- `GET /healthz` returns a simple readiness payload.

## Game session

- `POST /api/v1/game/start-game` creates a new session.
- `POST /api/v1/game/submit-prompt` evaluates a prompt and returns the outcome.

## Authentication

- The backend accepts an `X-API-Key` header when `API_KEY` is configured.
- Public health endpoints remain accessible without credentials.
