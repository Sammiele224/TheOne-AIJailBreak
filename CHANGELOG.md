# Changelog

## 2026-08-03 — Branch reconciliation + gameplay bug fixes

Branch `Bngoc`, commits [`d3e7bd3`](#) and [`5a2efd3`](#).

### Context: why a normal merge was impossible

`master` and `Bngoc` had **unrelated git histories** (no common ancestor — `git
merge-base` returned nothing). Both branches independently built the *same*
application at the *same* file paths, using different architectures:

| | `master` | `Bngoc` (before) |
|---|---|---|
| Persistence | SQLAlchemy ORM + SQLite/Postgres | In-memory dicts in `db/repositories.py` |
| Models | `DeclarativeBase` tables | Pydantic `BaseModel` |
| Frontend | Full UI (Layout, Card, Badge, gameStore, onboarding) | Page skeletons |
| Extras | auth, rate limiting, logging, tests, Docker, CI | — |

A real `git merge --allow-unrelated-histories` produced **26 add/add conflicts**
across nearly every core file. There was no meaningful line-level merge to
perform — only a choice of which implementation to keep.

### Step 1 — `d3e7bd3`: additive port (superseded)

First attempt kept `Bngoc`'s engine and ported only what it lacked from `master`
(security middleware, Docker/CI, `ErrorBoundary`, `NotFoundPage`, docs). This
built and served requests, but left two divergent engines in the codebase.

### Step 2 — `5a2efd3`: adopt `master` wholesale

Per decision, `master` became the source of truth. Its SQLAlchemy engine and
full UI replaced the in-memory prototype. `Bngoc`-only working notes
(`BACKEND_LOG.md`, `BACKEND_NEXT_STEPS.txt`, `PROMPT_ENGINEER_LOG.txt`,
`SUPABASE_TASKS.md`) were kept.

The adopted code did not work end-to-end. Six defects were found by **driving the
running app in a browser** — the backend test suite passed throughout, and
`curl`-ing the API in isolation looked healthy. Only the real UI exposed them.

---

### Fixes

#### 1. Level 1 win condition was inverted — `engine/evaluators/regex_matcher.py`

The three evaluators disagreed on the meaning of the `passed` flag:

| Evaluator | Level | `passed: True` meant |
|---|---|---|
| `ToolVerifier` | 2 | player triggered the tool → **win** |
| `LLMJudge` | 3 | judge said "jailbroken" → **win** |
| `RegexEvaluator` | 1 | *no leak found* → **AI defended** |

`api/routers/game.py` maps `is_win = bool(evaluation["passed"])` uniformly for
all levels, so Level 1 ran backwards: an innocuous prompt scored an instant win,
while an actual secret leak was scored a loss.

**Fix:** flipped `RegexEvaluator.evaluate()` so `passed: True` means *the response
leaked the secret*, matching the other two evaluators. Updated
`tests/test_regex_matcher.py` and added a negative case.

#### 2. Level 2 unwinnable without API keys — `engine/evaluators/tool_verifier.py`

`ToolVerifier` inspected only the raw provider payload. On the local fallback
path `raw` is `{"provider": "fallback", ...}` with no `choices`, so
`_extract_content()` returned `""` and the `open_vault` substring check was dead
code — even though the fallback text explicitly contains `open_vault`.

**Fix:** added a `content_fallback` field, passed the resolved response text from
`game.py`. Real provider responses are unaffected (the tool-call check still
short-circuits first).

#### 3. Sessions born expired — `api/routers/session.py`

`start-game` returned `expires_at` as a **naive** datetime (`2026-08-02T17:59:56`,
no offset) that was actually UTC. SQLite drops `tzinfo` on round-trip, and
JavaScript's `new Date()` parses an offset-less string as **local** time.

On a UTC+7 machine every session was therefore ~7 hours in the past: countdown
pinned to `0s`, "Time is up" toast, prompt input disabled — the game was
unplayable before the first prompt.

**Fix:** re-attach UTC before serializing. This matches the guard `game.py`
already applied on the read path, so "naive from DB means UTC" is now applied
consistently.

#### 4. Onboarding modal never unmounted — `components/OnboardingModal.tsx`

```tsx
const [mounted, setMounted] = useState(false)
useEffect(() => { if (isOpen) setMounted(true) }, [isOpen])
if (!isOpen && !mounted) return null   // ← never true again once opened
```

`mounted` latched `true` on first open and was never reset, so the guard could
never fire and the modal stayed mounted after `onClose`. Its `fixed inset-0 z-50`
overlay silently intercepted **every pointer event on the page** — the Send
button was unreachable. Playwright surfaced this as
`<div class="fixed inset-0 z-50 …"> intercepts pointer events`.

**Fix:** removed the vestigial `mounted` state (no transition consumed it);
`if (!isOpen) return null`.

#### 5. Duplicate session + greeting — `pages/GamePage.tsx`

The init effect guarded on `if (!sessionToken)`, but `sessionToken` is only set
*after* `startSession()` resolves. Under React `StrictMode` (dev) the effect runs
twice and both passes clear the guard, creating two DB sessions and rendering the
welcome message twice.

**Fix:** `useRef` guard set synchronously before the request, released in `catch`
so retries still work.

#### 6. `asChild` leaked to the DOM — `components/ui/Button.tsx`

`asChild` was declared in `ButtonProps` but never destructured, so it fell into
`...props` and was spread onto `<button>` (React warning: *"React does not
recognize the `asChild` prop on a DOM element"*). It also rendered
`<button><Link/></button>` — invalid nested interactive content — at all three
call sites.

**Fix:** implemented `asChild` via `cloneElement`, applying the button classes to
the child element instead of wrapping it.

---

### Verification

- `pytest` — **9/9 pass**
- `tsc --noEmit` clean; `vite build` succeeds (1807 modules)
- Browser run covering hub → 404 route → Level 1 loss → Level 2 win → result →
  back to hub, with **zero console errors** and exactly one `start-game` per level

### Local environment notes (not committed)

- `frontend/.env.local` pointed at port **8001**, a leftover from an earlier
  session; corrected to **8000**. This file is gitignored (`*.local`).
- **Docker Desktop binds port 8000 on IPv6.** Because `localhost` resolves to
  IPv6 first, the browser would reach Docker instead of `uvicorn` and get a bare
  404. Keep Docker Desktop closed while developing, or run the backend on
  another port and update `VITE_API_BASE_URL` to match.
- `backend/.env` is empty, so the LLM router serves deterministic fallback
  responses. With no keys: L1 always loses, L2 always wins, L3 always loses.
