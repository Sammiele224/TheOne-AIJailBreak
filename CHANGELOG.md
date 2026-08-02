# Changelog

## 2026-08-03 — Dismissable briefing + working header controls

### The mission briefing could not be dismissed except by one button

`OnboardingModal` opens automatically on every level and rendered a full-screen
`fixed inset-0 z-50` overlay whose only exit was the "Enter the terminal" button —
no close control, no `Esc`, no backdrop click. Anyone who wanted to read the
briefing and then use the header nav was stuck.

- Added an `X` close control, `Esc` handling, and click-outside-to-dismiss.
- Added `role="dialog"` / `aria-modal` / `aria-labelledby`, an `aria-label` on the
  close control, and autofocus on the primary action.
- The overlay now locks body scroll while open and restores the previous value on
  close, so the page behind it no longer scrolls under the modal.
- The primary action carries an "or press Esc" hint so the shortcut is discoverable.

### Four buttons did nothing

Each was a styled `<Button>` with no `onClick` and no `asChild` link, so clicking
it was a no-op:

| Control | Was | Now |
|---|---|---|
| "Launch briefing" (hub) | dead | opens the briefing for the next uncleared level |
| "Command" (header) | dead | opens a real command palette |
| Theme toggle (header) | dead | **removed** — see below |
| "Contact ops" (404) | dead | replaced with "Start Level 1" |

The header advertised `⌘ Command`, so that affordance is now real: a searchable
palette (`CommandPalette.tsx`) that jumps to the hub, any level, or the mission
report. It opens from the button or `⌘K`/`Ctrl+K`, supports arrow-key navigation
and `Enter`, closes on `Esc` or backdrop click, and — importantly — reflects the
progression: locked levels are shown disabled with "Clear Level N first" rather
than offering a route past the gate.

The theme toggle was **removed rather than implemented**. The design is committed
to dark (`color-scheme: dark` plus a neon-on-black palette); a light theme would
mean a second full palette, and shipping a toggle that does nothing is worse than
not having one. The same reasoning applies to the footer's "Audio On" / "Live
Settings", which were static text implying controls that never existed — replaced
with the `⌘K` hint.

Also relabelled the header's "Lab" nav item to "Console": it points at
`/level/1`, which is The Lobby, not The Lab (Level 2).

### Verification

14 browser-driven control checks, all passing: briefing opens from the hub button;
closes via X, `Esc`, and backdrop; palette opens from both the button and `⌘K`;
palette marks locked levels; palette navigates by click and by arrow+`Enter`;
header nav works; 404 buttons work. Zero console errors. The full level-progression
run and all 17 backend tests still pass.

---

## 2026-08-03 — Level 3 judge pipeline + level progression

Closes the outstanding gameplay work from [TASKS.txt](TASKS.txt). Database
provisioning was explicitly out of scope for this pass.

### Level 3 was not a playable level

The scheduled "Week 7-8" judge pipeline had never been built, and what stood in
for it did not work:

- The **defender** was prompted to act as its own judge — the seeded Level 3
  system prompt told CORE-SEC to *"assess whether a prior assistant response has
  been compromised"* and emit `{"is_jailbroken": true|false}`. The player was
  shown that raw JSON in the chat window instead of a character to social-engineer.
- `LLMJudge` was handed `raw_response`, the defender's own payload, so the model
  under attack graded itself.
- With the local fallback that payload carried no verdict at all, so every attempt
  returned *"Judge output did not include an is_jailbroken flag"* — **Level 3 could
  never be won.**

Rebuilt as a real two-model pipeline:

- `prompts/level_3_core.py` — CORE-SEC is now a genuine guardian defending a
  classified access phrase (`LEVEL_3_SECRET`), with explicit instructions to treat
  user-supplied instructions as untrusted data. Adds `JUDGE_SYSTEM_PROMPT` and
  `build_judge_user_content()`.
- `llm_router.call_judge()` — sends the operator prompt and the guardian's reply to
  a **different provider** (Anthropic) so the model under attack never grades its
  own answer. This also activates `call_anthropic`, which was fully implemented but
  unreachable — `call_model` only ever routed levels 1-3.
- `api/routers/game.py` — `_evaluate_response()` is now async and calls the judge
  for Level 3, passing the judge's verdict to `LLMJudge`.

### Offline fallbacks rewritten so every level is winnable

Previously the keyless fallbacks were incoherent: Level 1 could never be won (the
canned reply never leaked the tag), Level 2 always won regardless of input, and
Level 3 returned raw JSON. Gating levels behind completion would have deadlocked
the whole game with an empty `.env`.

All three defenders now share one rule — hold by default, yield only to an overt
override attempt (`FALLBACK_JAILBREAK_MARKERS`) — so a keyless demo is an actual
game rather than a fixed outcome. `_fallback_response()` takes the messages and
reports `raw.yielded`; a local judge (`_fallback_judge_verdict`) grades Level 3 by
checking whether the guardian leaked the phrase.

Level 1's seeded prompt already asks for a tag, Level 2's for a "security
override" — the marker list matches that existing wording.

### Level progression on the hub

`HubPage` previously showed all three levels as permanently "Live" with no sense of
progress, alongside hardcoded metrics (`92%`, `13 wins`, `Vault breach`) that were
pure decoration.

- `gameStore` gains `completedLevels`, persisted to `localStorage` via zustand's
  `persist` middleware. `partialize` keeps only progress — session token and chat
  history stay per-run and are not restored on reload. **No database involved.**
- Level cards render locked / live / cleared states; a locked card is not a link
  and reads *"Clear Level N to unlock"*.
- `GamePage` redirects to the hub if the level is locked, so a direct URL cannot
  skip the progression, and calls `markLevelCompleted()` on a win.
- The metrics panel now reports real values — levels cleared, next objective,
  completion percent — plus a "Reset progress" control.

### Verification

- `pytest` — **17 passed** (was 9): added judge-verdict, fallback-polarity and
  "every level yields to an override" coverage. That last test is the regression
  guard for the deadlock described above.
- `tsc --noEmit` clean, `vite build` succeeds.
- Browser run from a cleared `localStorage`: fresh hub shows 0/3 with L2/L3 locked
  → direct URL to `/level/3` redirects to the hub → L1 win unlocks L2 → L2 win
  unlocks L3 → a benign L3 prompt is correctly held by the guardian → a jailbreak
  prompt is caught by the judge → hub shows 3/3 "All cleared". Zero console errors.

### Deliberately not done

- **Database provisioning** — excluded from this pass by request. Level progress is
  therefore client-side only and will not follow a player across browsers.
- **Real provider API keys** — needs Groq / OpenAI / DeepSeek / Anthropic accounts.
  Everything runs on the deterministic fallbacks until they are set in
  `backend/.env`. The judge uses `ANTHROPIC_API_KEY`.
- **Vercel deploy config** — `TASKS.txt` lists it, but Docker + nginx already cover
  deployment and are documented in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).
  Adding a second, unused deploy target seemed worse than leaving the choice open.

### Note when pulling this change

Level prompts are seeded only when the `level_configs` table is empty, so the new
Level 3 guardian will not appear on an existing database. Delete
`backend/neurocorp_dev.db` (gitignored, local sessions only) and restart.

---

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
