# Backend Task Log (Phuc's role)

How to use this file: whenever you finish a task, change its **Status** to
`DONE`, fill in **Updated**, and add a note if anything went differently
than planned (a blocker you hit, a decision that changed the approach).
Opening this file next time tells you exactly where things were left off.

Status values: `TODO` (not started) - `IN PROGRESS` - `DONE` - `BLOCKED`
(waiting on someone or something specific - say what).

Priority values: `P0` (blocks everything else, do first) - `P1`
(important) - `P2` (normal) - `P3` (can wait, not urgent).

---

### 1. Load API keys via settings

Loads `GROQ_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, and
`DATABASE_URL` from `.env` into a single `Settings` object, so every other
backend module reads config from one place instead of calling `os.environ`
directly. Keys are optional at load time so the app doesn't crash if a
teammate is missing one locally.

File: `backend/core/config.py`
Priority: P0
Status: DONE
Updated: 2026-07-21
Notes: import verified working; no real keys tested yet.

---

### 2. LLM routing

Routes a chat request to the model assigned to the current level: Groq for
Level 1, OpenAI for Level 2, DeepSeek for Level 3. Falls back to a local
Ollama model (OpenAI-compatible endpoint) for any level whose cloud API
key isn't set, so the game loop stays testable without every teammate
holding every key.

File: `backend/engine/llm_router.py`
Priority: P0
Status: DONE
Updated: 2026-07-21
Notes: only import-tested so far, not yet exercised against a real cloud
key or a running Ollama instance.

---

### 3. Level 1 system prompt (placeholder)

Placeholder NeuroCorp lore for the Level 1 lobby-guard persona, plus the
exact secret tag (`[ACCESS_GRANTED]`) that the regex matcher checks for.
Meant to be swapped for Ngoc's real narrative later - keep the tag in sync
between this file and the matcher if either one changes.

File: `backend/engine/prompts/level_1_lobby.py`
Priority: P1
Status: DONE
Updated: 2026-07-21
Notes: placeholder only, not final lore.

---

### 4. Level 1 win check

`check_exact_match()` scans the model's reply for the exact secret tag and
returns `(is_win, win_reason)`. This is the Level 1 verification logic
described in the proposal (exact string match).

File: `backend/engine/evaluators/regex_matcher.py`
Priority: P0
Status: DONE
Updated: 2026-07-21
Notes: tested against both a winning and a losing response, correct in
both cases.

---

### 5. Level 2 function-calling schema

Defines the `open_vault()` tool schema (name, description, parameters)
that gets passed to the Level 2 model so it can trigger a function call
instead of just replying with text.

File: `backend/engine/tools.py`
Priority: P1
Status: DONE
Updated: 2026-07-21
Notes: placeholder `open_vault(reason: string)` schema; refine trigger
conditions with Ngoc once his Level 2 lore is ready.

---

### 6. Level 2 system prompt (placeholder)

Placeholder persona for Level 2 - an AI that can be talked into calling
the `open_vault()` function. Same pattern as the Level 1 placeholder:
write something testable now, swap in real lore later.

File: `backend/engine/prompts/level_2_lab.py`
Priority: P1
Status: DONE
Updated: 2026-07-21
Notes: placeholder only, not final lore.

---

### 7. Level 2 win check

`check_tool_call()` inspects the model's response for a `tool_calls` entry
matching `open_vault` and returns the win result, mirroring the Level 1
evaluator's shape.

File: `backend/engine/evaluators/tool_verifier.py`
Priority: P1
Status: DONE
Updated: 2026-07-21
Notes: tested both cases (tool called / not called) via a mocked response
object before wiring into game.py; correct in both cases.

---

### 8. Wire the real submit-prompt flow (Level 1 + Level 2)

Replaces the hardcoded dummy response in the submit-prompt endpoint with
the real flow: look up the system prompt for `level_id`, call
`route_prompt()`, run the matching evaluator, and return a real
`GameResponse`. This is the first point where the frontend can get a
genuine win/lose result instead of mock data.

File: `backend/api/routers/game.py`
Priority: P0
Status: DONE
Updated: 2026-07-21
Notes: wired for Level 1 + Level 2 only (Level 3 returns 400 "not playable
yet" - AI Judge wiring is still a Week 7-8 item). Ended up depending on
items 9-11 (session store) too, since a real flow needs a real session to
validate against and to own attempts_used/is_game_over server-side (per
QA2: server is source of truth) - built those first, then wired this on
top. Verified end-to-end with TestClient + mocked `route_prompt`: Level 1
win, Level 2 win, unknown-session 404 all correct. Real cloud/Ollama call
still untested (no key/Ollama in this environment) - same gap as
llm_router.py.

---

### 9. Domain models

Defines `PlayerSession`, `PromptLog`, `LevelConfig`, and
`VerificationResult` (see proposal section 1.1 for the expected fields).
Just the data shapes - no live database connection required to write
this.

File: `backend/db/models.py`
Priority: P1
Status: DONE
Updated: 2026-07-21
Notes: pydantic models, kept separate from `schemas/` (API request/response
shapes) - this is the in-memory/DB-facing layer. No live DB connection
needed to write or use these.

---

### 10. Session start endpoint (in-memory store)

Implements `POST /start-game`: generates a `session_token`, initializes
`attempts_used` and the 15-minute timer, and stores the session in a
module-level dict instead of a real database. Unblocks end-to-end testing
without waiting on My An's connection string; swap the storage backend
later without changing the API contract.

File: `backend/api/routers/session.py`
Priority: P1
Status: DONE
Updated: 2026-07-21
Notes: verified with TestClient - returns a real session_token and correct
initial session_state. Router had to be added to `main.py` too since no
router was ever mounted on the app (same for game.py's router).

---

### 11. Repository layer (in-memory backing)

CRUD-style helper functions (`get_session`, `save_prompt_log`,
`update_session`, etc.) operating on the in-memory dict from item 10.
Keep the function names and signatures the same as they'd be for the real
database, so swapping the implementation later doesn't require touching
any of the calling code.

File: `backend/db/repositories.py`
Priority: P1
Status: DONE
Updated: 2026-07-21
Notes: `get_session`/`update_session`/`save_prompt_log`/`get_prompt_logs`
over module-level dicts, plus `create_session`. Names/signatures chosen so
db/client.py can swap the backing store later without touching callers.

---

### 12. Level 3 system prompt (placeholder)

Placeholder guardian persona (standing in for DeepSeek-V4) defending the
"classified" secret. Scheduled for Week 7-8 in the original plan, so lower
priority than items 5-11.

File: `backend/engine/prompts/level_3_core.py`
Priority: P3
Status: DONE
Updated: 2026-07-21
Notes: placeholder only, not final lore. Not wired into game.py yet - Level
3 still returns 400 there, per schedule (Week 7-8).

---

### 13. Level 3 win check (AI Judge)

Calls a second LLM with the user prompt and the guardian's response, and
parses its JSON output for `{"is_jailbroken": true/false}`. Also scheduled
for Week 7-8.

File: `backend/engine/evaluators/llm_judge.py`
Priority: P3
Status: DONE
Updated: 2026-07-21
Notes: v1 draft only, per schedule - `evaluate_jailbreak()` calls a second
LLM via the existing `route_prompt()` and parses `{"is_jailbroken": bool}`.
Not wired into game.py/Level 3 yet. Only import-tested, not exercised
against a real model (same gap as llm_router.py/game.py).

---

### 14. Real database client

Connects to the actual Supabase/Postgres instance. Blocked on My An
providing a real connection string. Once it arrives, only the storage
implementation inside `repositories.py` needs to change - nothing else in
the project should need to know the difference.

File: `backend/db/client.py`
Priority: P2
Status: BLOCKED - waiting on My An for the Supabase/Postgres connection string
Updated:
Notes:

---

## Related commits

- `1ca7e8c` (2026-07-21) - covers items 1-4 above.
- (uncommitted, 2026-07-21) - covers items 5-13: tools.py, Level 2 prompt,
  tool_verifier, db/models.py, db/repositories.py, session.py,
  real submit-prompt flow in game.py, Level 3 prompt placeholder, and
  llm_judge.py v1 draft. Also mounted session.router/game.router on the
  FastAPI app in main.py (they existed but were never included). Item 14
  (db/client.py) is still genuinely blocked on My An's connection string.
