# Documentation

Reference docs for TheOne AI JailBreak. Start with the knowledge base; the rest
are operational references.

| Document | What it covers |
|---|---|
| [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) | How the system actually works: level/evaluator behavior, request flow, backend and frontend file maps, gotchas |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Endpoint list and authentication |
| [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) | Every variable the backend and frontend read |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Docker Compose and production deployment notes |

## Team worklog

[worklog/](worklog/) holds the team's task tracking and per-role work logs.
These churn week to week and describe intent rather than current behavior — when
they disagree with the reference docs above, the reference docs win.

| Document | Owner / scope |
|---|---|
| [worklog/BACKEND_LOG.md](worklog/BACKEND_LOG.md) | Backend task log with statuses |
| [worklog/SUPABASE_TASKS.md](worklog/SUPABASE_TASKS.md) | Supabase/Postgres migration plan (expands item 14 of the backend log) |
| [worklog/PROMPT_ENGINEER_LOG.txt](worklog/PROMPT_ENGINEER_LOG.txt) | Prompt engineering track work log |
