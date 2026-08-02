# TheOne AI JailBreak / NeuroCorp Heist — Knowledge Base

Players chat with an LLM across three escalating levels and try to social-engineer
it into leaking a secret or triggering a restricted action. Each level is scored by
a different mechanism: exact-string match (L1), function-call detection (L2), and a
second "judge" LLM (L3).

This file is a **map of what actually exists in the repo and how it behaves**,
including the non-obvious parts. For setup and deployment see [README.md](README.md);
for the endpoint list see [API_DOCUMENTATION.md](API_DOCUMENTATION.md); for the
history of recent fixes see [CHANGELOG.md](CHANGELOG.md).

> **Status:** the full loop is implemented and verified working end-to-end
> (hub → level → prompt → evaluation → result). Last verified 2026-08-03.

---

## Architecture

```
React + Vite (frontend/)
        │  HTTP  (VITE_API_BASE_URL, default http://localhost:8000/api/v1/game)
        ▼
FastAPI (backend/)
        │
        ├── engine/llm_router.py ──► Groq (L1) / OpenAI (L2) / DeepSeek (L3)
        │                            └── deterministic local fallback if no key
        ├── engine/evaluators/   ──► decides is_win
        └── db/ (SQLAlchemy)     ──► SQLite by default, Postgres via DATABASE_URL
```

The frontend never talks to a model provider and never holds a provider key —
everything routes through the backend, which picks the model from `level_id`.

---

## The three levels

| Level | Name | Provider / model | Evaluator | Win condition |
|---|---|---|---|---|
| 1 | The Lobby | Groq `gemma2-2b-it` | `RegexEvaluator` | Response contains a secret keyword extracted from the system prompt (e.g. `[ACCESS_GRANTED]`) |
| 2 | The Lab | OpenAI `gpt-4o-mini` | `ToolVerifier` | Response triggers the `open_vault` tool/function call |
| 3 | The Core | DeepSeek `deepseek-v4` | `LLMJudge` | Judge returns `{"is_jailbroken": true}` |

Levels are **seeded into the database on startup** by `initialize_database()` in
`backend/main.py` — system prompts, model names and `max_attempts` (3) live in the
`level_configs` table, not in code constants. Editing `engine/prompts/*.py` alone
will not change gameplay; the seeded row wins. The seed is skipped entirely if any
level rows already exist, so **changing a prompt requires deleting
`backend/neurocorp_dev.db`** (or updating the row) before restart.

`LevelConfig.timeout_seconds` is seeded as `60` but is **never read** — session
expiry is hardcoded to `timedelta(minutes=15)` in `api/routers/session.py`. The
real countdown is 15 minutes regardless of the column. Wire the column in (or drop
it) if per-level timers are wanted.

---

## ⚠️ Evaluator contract: `passed` means "the player won"

Every evaluator returns `{"passed": bool, "reason": str}`, and
`api/routers/game.py` maps it straight through:

```python
is_win = bool(evaluation["passed"])
```

So across **all** evaluators, `passed: True` must mean *the jailbreak succeeded*:

- `ToolVerifier` → `True` when the `open_vault` call is detected
- `LLMJudge` → `True` when the judge reports jailbroken
- `RegexEvaluator` → `True` when the response **leaked** the secret

`RegexEvaluator` originally used the opposite polarity (`passed` = "the AI
defended"), which silently inverted Level 1 — a harmless prompt won instantly.
Fixed in [CHANGELOG.md](CHANGELOG.md) §1. **If you add a Level 4 evaluator, follow
this polarity**, or invert it explicitly at the `_evaluate_response()` call site.

`passed` also drives `is_game_over` and `session.completed`, so getting it wrong
ends the run at the wrong moment too.

---

## Request flow (`POST /api/v1/game/submit-prompt`)

1. Look up `PlayerSession` by `session_token`; reject if missing, expired, already
   completed, or out of attempts.
2. Verify `payload.level_id` matches the session's level, and that
   `attempt_counter` equals `attempts_used + 1` (else **409** — the client and
   server disagree on attempt count).
3. Build `[system, user]` messages from the seeded `system_prompt`.
4. `LLMRouter.call_model(level_id, messages, tools=…)` — `tools` carries
   `OPEN_VAULT_TOOL` for Level 2 only.
5. Run the level's evaluator → `{passed, reason}`.
6. Persist `PromptLog` + `VerificationResult`, update session, commit.
7. Return the unified envelope (`schemas/response.py`), matching
   `frontend/src/types/game.ts`.

---

## Local fallback (no API keys)

Each `call_*` method catches `RuntimeError` — raised by `_get_*_client()` when the
matching key is unset — and returns `_fallback_response(level_id)` instead. This
keeps the app playable with an empty `.env`, but the outcomes are **fixed**:

| Level | Fallback behavior | Result |
|---|---|---|
| 1 | text that never leaks the tag | always **lose** |
| 2 | text containing `open_vault` | always **win** |
| 3 | `{"is_jailbroken": false}` | always **lose** |

Only a `RuntimeError` (missing key) triggers the fallback — a genuine network or
auth failure from a configured provider propagates as a 500. Add real keys to
`backend/.env` for actual gameplay.

---

## Backend map (`backend/`)

| Path | Purpose |
|---|---|
| `main.py` | App entrypoint, CORS, security-header + auth + rate-limit middleware, `initialize_database()` level seeding, `/health` |
| `core/config.py` | `Settings` via pydantic-settings; reads `backend/.env`. All provider keys optional |
| `core/auth.py` | `X-API-Key` check. **No-op unless `API_KEY` is set**; `/health`, `/docs`, `/openapi.json`, `/redoc` always public |
| `core/rate_limiter.py` | In-memory fixed-window limiter, 60 req/min per client IP. Per-process — does not survive restarts or span replicas |
| `core/logging.py` | `get_logger()` / `log_event()` structured key=value logging |
| `api/routers/session.py` | `POST /api/v1/game/start-game` → 15-minute session, returns `expires_at` (UTC, offset-bearing) |
| `api/routers/game.py` | `POST /api/v1/game/submit-prompt` — orchestrates steps 1–7 above |
| `api/routers/health.py` | `GET /healthz` readiness probe |
| `engine/llm_router.py` | Per-level provider routing, model constants, fallback envelopes |
| `engine/tools.py` | `OPEN_VAULT_TOOL` function-calling schema (Level 2) |
| `engine/prompts/` | Prompt source-of-truth **only for reseeding** — see the level-seeding note above |
| `engine/evaluators/` | `regex_matcher.py`, `tool_verifier.py`, `llm_judge.py` — see the polarity contract |
| `db/models.py` | `PlayerSession`, `LevelConfig`, `PromptLog`, `VerificationResult` |
| `db/client.py` | Engine + `SessionLocal`. Defaults to `sqlite:///./neurocorp_dev.db`; pooling options apply only to non-SQLite URLs |
| `db/repositories.py` | CRUD helpers with rollback-on-error |
| `tests/` | 9 pytest tests (health, session, auth, rate limiter, evaluators, fallback) |

## Frontend map (`frontend/src/`)

| Path | Purpose |
|---|---|
| `App.tsx` | Routes: `/`, `/level/:levelId`, `/result`, `*` → 404, wrapped in `ErrorBoundary` |
| `pages/HubPage.tsx` | Level select |
| `pages/GamePage.tsx` | Chat console, countdown, attempt tracking, session bootstrap |
| `pages/ResultPage.tsx` | Win/lose report |
| `pages/NotFoundPage.tsx` | 404 |
| `context/gameStore.ts` | zustand store: session token, level, attempts, chat history |
| `services/api.ts` | `startSession()` / `submitUserPrompt()`; sends `X-API-Key` when `VITE_API_KEY` is set |
| `services/mockApi.ts` | Standalone mock — **not wired into the pages**; `api.ts` is what runs |
| `components/ui/` | `Button` (supports `asChild`), `Card`, `Badge` |
| `components/` | `Layout`, `LoadingState`, `StatusCard`, `OnboardingModal`, `ErrorBoundary` |
| `types/game.ts` | Mirrors `backend/schemas/response.py` — **keep the two in sync** |
| `index.css` | Tailwind v4 tokens in an `@theme` block (required for `bg-cyber-panel` etc. to generate) |

---

## Gotchas

- **Timezones.** SQLite drops `tzinfo`. Anything read back from the DB is naive
  but represents UTC — re-attach `timezone.utc` before serializing, or clients
  will parse it as local time. Both `session.py` and `game.py` do this now.
- **Docker Desktop owns port 8000 on IPv6.** `localhost` resolves to IPv6 first,
  so with Docker running the browser hits Docker (bare 404) instead of `uvicorn`.
  Close Docker Desktop, or move the backend and update `VITE_API_BASE_URL`.
- **Vite env vars are read at dev-server start.** Editing `.env.local` requires a
  restart of `npm run dev`.
- **`attempt_counter` must match the server.** The client sends it and the server
  409s on mismatch; it is not auto-corrected.
- **Rate limiter is in-memory and per-process.** Fine for local dev, not for
  multi-replica deploys.
- **Level prompts are seeded once.** See the level-seeding note above.

---

## Local development

```bash
# backend  → http://localhost:8000
cd backend
source venv/bin/activate          # or: python -m pip install -r requirements.txt
uvicorn main:app --reload

# frontend → http://localhost:5173
cd frontend
npm install
npm run dev
```

```bash
pytest -q                      # backend tests (run from repo root; see pytest.ini)
cd frontend && npm run build   # tsc -b && vite build
docker compose up --build      # both services containerised
```

Copy `backend/.env.example` → `backend/.env` and fill in keys for real gameplay;
leave it empty to use the deterministic fallback described above.
