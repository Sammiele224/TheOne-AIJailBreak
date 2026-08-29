# Deployment Guide

## Prerequisites

- Docker and Docker Compose
- Optional: a real API key for a model provider

## Local deployment

```bash
docker compose up --build
```

## Environment variables

Set the following variables before deployment:

- `API_KEY`: shared secret for protecting non-public API routes
- `ALLOWED_ORIGINS`: comma-separated allowed frontend origins
- `DATABASE_URL`: PostgreSQL or SQLite URL for persistence
- `DEBUG`: set to `false` in production
- `GROQ_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`: optional provider credentials

## Production notes

- Mount a persistent volume for `/app/data` in the backend container.
- Prefer PostgreSQL over SQLite for multi-instance deployments.
- Keep `API_KEY` in a secret manager.
