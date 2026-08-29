# Supabase / Postgres Work — Detailed Task List

Scope: everything needed to move persistence from the in-memory dicts in
[backend/db/repositories.py](../../backend/db/repositories.py) to a real
Supabase/Postgres instance. Split out of item 14 of
[BACKEND_LOG.md](BACKEND_LOG.md) because that one line ("db/client.py — blocked
on My An's connection string") actually hides ~10 discrete pieces of work.

**Design contract to preserve:** the repository function names and signatures in
`db/repositories.py` must NOT change. Callers (`api/routers/session.py`,
`api/routers/game.py`) import `create_session`, `get_session`,
`update_session`, `save_prompt_log`, `get_prompt_logs` and must keep working
untouched when the storage backend is swapped. Everything below is written to
honor that.

Status values: `TODO` · `IN PROGRESS` · `DONE` · `BLOCKED` (say on what).
Priority: `P0` (unblocks everything) · `P1` · `P2` · `P3`.

---

## S0. Provision the Supabase project — **owner: My An (DevOps/QA)**

Priority: P0
Status: BLOCKED — this is the root blocker for S3–S9.
Blocks: everything below.

- Create the Supabase project (region close to the team / Vercel deploy).
- From **Project Settings → Database**, capture BOTH connection strings:
  - **Session pooler / direct** (`...supabase.co:5432`) — for migrations.
  - **Transaction pooler** (`...pooler.supabase.com:6543`) — for the app
    runtime (serverless-friendly).
- Also capture, from **Project Settings → API**: `Project URL`, `anon` key,
  and `service_role` key (only needed if we use the `supabase-py` client
  instead of a raw Postgres driver — see S2).
- Hand the connection string(s) + keys to Phuc **via a secret channel, never in
  git**. Confirm `backend/.env` is gitignored (it is — verify anyway).

Deliverable: values pasted into `backend/.env` locally + stored in the team
password manager / Vercel env vars for deploy.

---

## S1. Decide the schema (tables + columns) — **owner: Phuc + My An**

Priority: P0 (can be done in parallel with S0, no live DB needed)
Status: TODO
Depends on: nothing (design task).

Derive the DDL directly from the existing Pydantic models in
[backend/db/models.py](../../backend/db/models.py) so the DB rows map 1:1 to the app
models. Proposed tables:

**`player_sessions`**
| column | type | notes |
|---|---|---|
| `session_token` | `text primary key` | matches `PlayerSession.session_token` |
| `current_level` | `int not null default 1` | |
| `attempts_used` | `int not null default 0` | |
| `max_attempts` | `int not null default 20` | |
| `is_game_over` | `boolean not null default false` | |
| `created_at` | `timestamptz not null default now()` | |
| `expires_at` | `timestamptz not null` | 15-min timer end |

**`prompt_logs`**
| column | type | notes |
|---|---|---|
| `message_id` | `text primary key` | matches `PromptLog.message_id` |
| `session_token` | `text not null references player_sessions(session_token)` | FK |
| `level_id` | `int not null` | |
| `user_prompt` | `text not null` | |
| `ai_response` | `text not null` | |
| `is_win` | `boolean not null` | |
| `win_reason` | `text not null` | |
| `latency_ms` | `int not null` | |
| `created_at` | `timestamptz not null default now()` | |

**`level_configs`** (optional — only if we want lore/config in the DB instead of
in `engine/prompts/*.py`; `LevelConfig` model already exists). Recommend
**deferring** (P3) — prompts currently live in code and that's fine for now.

Index to add: `create index on prompt_logs (session_token);` — `get_prompt_logs`
filters by `session_token`.

Deliverable: a reviewed `schema.sql` (see S3).

---

## S2. Pick the driver + pin dependencies — **owner: Phuc**

Priority: P0
Status: TODO
Depends on: S1.

Current [backend/requirements.txt](../../backend/requirements.txt) has **no** Postgres
driver or Supabase client. Decision needed:

- **Option A (recommended): raw async Postgres** via `asyncpg` +
  `sqlalchemy[asyncio]` (or `asyncpg` alone with hand-written SQL). Keeps us on
  the connection string only, no extra Supabase SDK, works cleanly with FastAPI
  async endpoints (`session.py` / `game.py` are already `async def`).
- **Option B: `supabase-py`** client (uses the REST/PostgREST layer + API keys
  from S0). Simpler CRUD, but adds a heavier dep and a second auth surface.

Recommendation: **Option A** — the repository layer is already plain CRUD, and
we already carry a `DATABASE_URL` in [config.py](../../backend/core/config.py), not
API keys. Add to `requirements.txt` (pin versions):
```
asyncpg==<pin>
sqlalchemy==<pin>          # only if using the ORM/core; optional
```
Deliverable: updated + pinned `requirements.txt`, `pip install` verified.

---

## S3. Write migrations / `schema.sql` — **owner: Phuc**

Priority: P1
Status: TODO
Depends on: S1.

- Create `backend/db/schema.sql` with the DDL from S1 (tables, FK, index).
- Apply it to the Supabase instance (via the Supabase SQL editor or
  `psql "$DATABASE_URL" -f backend/db/schema.sql`).
- No heavyweight migration tool needed yet; if the schema starts churning,
  revisit Alembic (P3, out of scope for now).

Deliverable: `backend/db/schema.sql` committed; tables exist in Supabase.

---

## S4. Implement the DB client — **owner: Phuc** (this is the old "item 14")

Priority: P1
Status: BLOCKED on S0 (needs a real connection string) — code can be drafted now.
File: [backend/db/client.py](../../backend/db/client.py) (currently empty)

- Read `settings.database_url` from [core/config.py](../../backend/core/config.py)
  (field already exists).
- Create a single shared connection pool (`asyncpg.create_pool(...)`), created
  on FastAPI startup and closed on shutdown — wire via lifespan/startup hooks in
  [backend/main.py](../../backend/main.py).
- Expose a small accessor (e.g. `get_pool()` / an `acquire()` context manager)
  for `repositories.py` to use.
- Fail loudly with a clear message if `database_url` is unset **and** we're not
  intentionally in in-memory mode (see S5 fallback).

Deliverable: `client.py` that opens/closes a pool and hands out connections.

---

## S5. Swap `repositories.py` to the real backend — **owner: Phuc**

Priority: P1
Status: TODO
File: [backend/db/repositories.py](../../backend/db/repositories.py)
Depends on: S3, S4.

Replace the dict/list bodies with real SQL while keeping **exact same function
names and signatures**:

- `create_session(level_id, max_attempts, time_limit_seconds) -> PlayerSession`
  → `INSERT INTO player_sessions (...) VALUES (...) RETURNING *`, hydrate into
  the `PlayerSession` model.
- `get_session(session_token) -> PlayerSession | None`
  → `SELECT ... WHERE session_token = $1`.
- `update_session(session_token, **fields) -> PlayerSession`
  → dynamic `UPDATE player_sessions SET ... WHERE session_token = $1 RETURNING *`.
  Keep the `**fields` kwargs shape so `game.py` doesn't change.
- `save_prompt_log(log: PromptLog) -> None`
  → `INSERT INTO prompt_logs (...)`.
- `get_prompt_logs(session_token) -> list[PromptLog]`
  → `SELECT ... WHERE session_token = $1 ORDER BY created_at`.

**Note:** these are currently sync functions called from `async def` endpoints.
With `asyncpg` they become `async def`. That means the two call sites need
`await`:
- `api/routers/session.py` → `session = await create_session(...)`
- `api/routers/game.py` → every `get_session` / `update_session` /
  `save_prompt_log` / `get_prompt_logs` call.
This is the ONE place the "no caller changes" contract bends (adding `await`);
flag it in the PR. Consider an env flag `USE_IN_MEMORY_DB=1` to keep the dict
backend available for teammates without DB access (see S8).

Deliverable: `repositories.py` backed by Postgres; two routers get `await`s.

---

## S6. Config + env wiring — **owner: Phuc + My An**

Priority: P1
Status: TODO
Depends on: S0.

- [backend/core/config.py](../../backend/core/config.py) already declares
  `database_url` — confirm it's actually read in `client.py` (S4).
- Update [backend/.env.example](../../backend/.env.example): `DATABASE_URL` is already
  listed; add a comment on which pooler URL to use, and (if Option B) the
  `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` keys.
- Add the same vars to the **Vercel / deploy** environment (coordinate with My
  An's deploy track in `TASKS.txt` (since removed)).

Deliverable: `.env.example` documents every DB var; real values in `.env` + Vercel.

---

## S7. Row Level Security / access hardening — **owner: My An + Phuc**

Priority: P2
Status: TODO
Depends on: S0, S3.

- The backend connects with a privileged Postgres role, so the frontend never
  touches Supabase directly (matches the architecture note in
  [KNOWLEDGE_BASE.md](../KNOWLEDGE_BASE.md): frontend → FastAPI only).
- Decide RLS posture: since only the backend connects, either keep RLS off on
  these tables (backend-only access) **or** enable RLS + a service-role policy
  as defense-in-depth. Document the choice.
- Ensure the `anon`/`public` API is NOT exposed for these tables if PostgREST is
  enabled by default.

Deliverable: documented RLS decision; no anon read/write on game tables.

---

## S8. Keep an in-memory fallback for keyless teammates — **owner: Phuc**

Priority: P2
Status: TODO
Depends on: S5.

Not everyone will have the connection string locally. Add a switch (e.g.
`USE_IN_MEMORY_DB` env var, default to in-memory when `DATABASE_URL` is unset)
so `repositories.py` can pick the dict backend or the Postgres backend. Mirrors
the existing Ollama fallback pattern in `llm_router.py` — the game loop stays
runnable without every secret.

Deliverable: backend runs both with and without `DATABASE_URL` set.

---

## S9. Test against the real instance — **owner: Phuc + My An (QA)**

Priority: P1
Status: TODO
Depends on: S4, S5.

- Round-trip test with a live connection: `POST /start-game` writes a row →
  `POST /submit-prompt` reads the session, writes a `prompt_logs` row, updates
  `attempts_used`/`is_game_over` → re-read reflects it.
- Verify expiry: a session past `expires_at` is treated as over.
- Verify FK + index behave (log insert with unknown `session_token` rejected).
- Existing `TestClient` tests (Level 1 win / Level 2 win / unknown session 404)
  still pass against the Postgres backend, not just the dict one.

Deliverable: green round-trip test notes appended to
[BACKEND_LOG.md](BACKEND_LOG.md) item 14.

---

## Suggested order

S0 (My An, unblocks all) ∥ S1 (schema design, no DB needed)
→ S2 (driver) → S3 (schema.sql applied) → S4 (client) → S5 (repositories + awaits)
→ S6 (env) → S9 (test). S7 (RLS) and S8 (fallback) fold in alongside S5–S6.

Critical path is **S0**: until My An hands over the connection string, S3–S9
can be written but not run. S1/S2/S4-draft can all proceed now.
