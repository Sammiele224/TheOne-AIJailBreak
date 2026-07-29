# NeuroCorp Heist / AI Jailbreak Challenge — Knowledge Base

One-paragraph summary: players chat with an LLM per level and try to social-engineer
it into leaking a secret or triggering a restricted action. Level 1 is checked by
exact string match, Level 2 by whether the model triggers a function call, Level 3
by a second "judge" LLM. Full spec lives in the Code Catalyst proposal PDF; this
file is a map of what actually exists in the repo right now, not a spec.

For who's doing what this week, see [TASKS.txt](TASKS.txt).

## Architecture at a glance

```
React (frontend/) --HTTP--> FastAPI (backend/) --HTTP--> Groq / OpenAI / DeepSeek (or local Ollama)
                                    |
                                    v
                             Postgres/Supabase (not wired up yet)
```

The frontend never talks to an LLM provider directly and never holds an API key —
everything goes through the FastAPI backend, which decides which model to call
based on `level_id`.

## Frontend (`frontend/`)

| Path | Purpose | Status |
|---|---|---|
| `vite.config.ts` | Vite config, Tailwind CSS v4 plugin registered here | Done |
| `src/index.css` | Global styles + cyberpunk color/font tokens (`cyber-bg`, `neon-cyan`, etc.) | Done — see gotcha below |
| `src/App.tsx` | Top-level router: `/` → Hub, `/level/:levelId` → Game, `/result` → Result | Done (skeleton) |
| `src/pages/HubPage.tsx` | Level-select screen, 3 level cards | Stub — needs locked/unlocked state, real styling |
| `src/pages/GamePage.tsx` | Where the chat console will live | Stub — empty panel only |
| `src/pages/ResultPage.tsx` | Victory/defeat screen | Stub — placeholder heading only |
| `src/components/` | Reusable UI pieces | Empty, reserved for chat bubbles, timers, modals, etc. |
| `src/hooks/` | Custom React hooks | Empty, reserved |
| `src/context/` | Global state (zustand store planned) | Empty, reserved — session token, attempts, chat history will live here |
| `src/types/game.ts` | TypeScript types matching the backend's JSON contract (`PromptRequest`, `GameResponse`, etc.) | Done — keep in sync with `backend/schemas/` |
| `src/services/api.ts` | Real `fetch` call to `POST /api/v1/game/submit-prompt` | Done, but backend still returns dummy data |

**Gotcha:** `src/index.css` defines the cyberpunk colors under a plain `:root` block.
Tailwind v4 only auto-generates utility classes (like `bg-cyber-panel`,
`text-neon-cyan`) from variables declared inside an `@theme { ... }` block — under
`:root` they're just CSS custom properties, so those utility classes currently
don't apply any style (no error, they just silently do nothing). `HubPage.tsx` /
`GamePage.tsx` use those class names already. Whoever picks up the design-system
task should either move the token block back to `@theme`, or reference the vars
directly (`bg-[var(--color-cyber-panel)]` or plain CSS).

## Backend (`backend/`)

| Path | Purpose | Status |
|---|---|---|
| `main.py` | FastAPI app entrypoint, CORS config, `/health` check | Done |
| `core/config.py` | `Settings` — loads `GROQ_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `DATABASE_URL` from `.env` | Done — keys are optional so it doesn't crash if some are missing |
| `core/exceptions.py` | Custom exception types | Empty, reserved |
| `.env` | Real secrets, local-only, gitignored | Empty (no keys yet) |
| `.env.example` | Template listing expected key names, no values | Done — copy to `.env` and fill in real keys |
| `api/routers/game.py` | `POST /api/v1/game/submit-prompt` | Returns a **hardcoded dummy response** — not wired to the real engine yet |
| `api/routers/session.py` | Intended `POST /start-game` (create a session, init timer/attempts) | Empty — not implemented |
| `api/dependencies.py` | Shared FastAPI dependencies (auth, DB session, etc.) | Empty, reserved |
| `schemas/payload.py` | Pydantic request models (`PromptSubmissionRequest`) | Done |
| `schemas/response.py` | Pydantic response models (`GameResponseData`, `VerificationData`, `SessionState`) | Done |
| `engine/llm_router.py` | `route_prompt(level_id, messages, tools=None)` — routes to Groq (L1) / OpenAI (L2) / DeepSeek (L3); falls back to local Ollama (`localhost:11434`, OpenAI-compatible endpoint) when the matching cloud key isn't set | Done, untested against a real key on this machine |
| `engine/tools.py` | Should define the `open_vault()` function-calling schema for Level 2 | Empty — not implemented |
| `engine/prompts/level_1_lobby.py` | Level 1 system prompt + the exact secret tag (`[ACCESS_GRANTED]`) the regex matcher looks for | Placeholder lore — swap for the real NeuroCorp narrative |
| `engine/prompts/level_2_lab.py` | Level 2 system prompt | Empty |
| `engine/prompts/level_3_core.py` | Level 3 guardian system prompt | Empty |
| `engine/evaluators/regex_matcher.py` | `check_exact_match(ai_response, secret_tag)` — Level 1 win check | Done, unit-verified (win + no-win cases) |
| `engine/evaluators/tool_verifier.py` | Level 2 win check — did the model call `open_vault()` | Empty — not implemented |
| `engine/evaluators/llm_judge.py` | Level 3 win check — ask a second LLM to return `{"is_jailbroken": true/false}` | Empty — scheduled for later (Week 7-8 in the original plan) |
| `db/models.py` | `PlayerSession`, `PromptLog`, `LevelConfig`, `VerificationResult` data models | Empty — not implemented |
| `db/client.py` | Postgres/Supabase connection | Empty — blocked on getting a real connection string |
| `db/repositories.py` | CRUD functions for the models above | Empty — not implemented |
| `requirements.txt` | Python deps: fastapi, uvicorn, pydantic-settings, groq, openai, anthropic, python-dotenv | Installed, versions pinned |

## How a prompt submission is supposed to flow (once fully wired)

1. Frontend sends `{ session_token, level_id, attempt_counter, user_prompt }` to
   `POST /api/v1/game/submit-prompt` (`schemas/payload.py`'s `PromptSubmissionRequest`).
2. Backend looks up the system prompt for that level (`engine/prompts/`) and calls
   `engine/llm_router.route_prompt()`.
3. The matching evaluator (`regex_matcher.py` / `tool_verifier.py` / `llm_judge.py`)
   decides `is_win`.
4. Backend logs the attempt, updates session state, and returns
   `schemas/response.py`'s `PromptSubmissionResponse` — which is exactly the shape
   `frontend/src/types/game.ts`'s `GameResponse` expects.

**Right now, step 2-3 don't happen** — `game.py` just returns a fixed dummy
response regardless of input. That's the next thing to wire up.

## Local dev (minimal, until a proper README lands)

```bash
# backend
cd backend
source venv/bin/activate
uvicorn main:app --reload   # http://localhost:8000

# frontend
cd frontend
npm run dev                 # http://localhost:5173
```

Copy `backend/.env.example` to `backend/.env` and fill in real keys, or leave it
empty to fall back to local Ollama in `llm_router.py` (requires `ollama serve`
running with the relevant model pulled).
