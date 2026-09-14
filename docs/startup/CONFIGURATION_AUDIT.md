# Configuration & Secret Audit

Audit date: 2026-09-13  
Prompt 3 update: 2026-09-13 — living contract in `CONFIGURATION_ARCHITECTURE.md` and `CONFIGURATION_CONTRACT.md`.

Policy: **do not print secret values**. If a secret appears committed, report file/pattern only.

---

## Configuration sources

| Source | Role |
|--------|------|
| `.env.example` | Documented placeholders for backend/frontend |
| `.env` (local) | Optional; loaded only in development (not production); **gitignored** |
| `frontend/.env.example` | Public + documented server-only notes |
| `frontend/.env.local` | Local public API URL; **gitignored** |
| `backend/app/core/config.py` | **Canonical** typed `Settings` loader |
| `frontend/lib/env.ts` | Public/server API base URL helpers |
| `docker-compose.yml` | Dev service env (placeholder DB creds; no `.env` COPY into image) |
| `alembic/env.py` | Migrations; `DATABASE_URL` from env |
| CI workflow env | `APP_ENV=test`, ephemeral Postgres creds |

---

## Secret handling verification (Prompt 3 re-check)

| Check | Result |
|-------|--------|
| `.env` tracked by git? | **No** |
| `frontend/.env.local` tracked? | **No** |
| Real API keys found committed? | **No** |
| Safe summary / `print_config` | Redacts secrets; covered by tests |

---

## Prompt 3 remediations applied

- Fail-fast production/CORS/log/path validation  
- Test isolation fixture + non-local DB guard  
- Explicit PUBLIC/INTERNAL/SECRET classification  
- Experiment params kept out of infrastructure env  
- Path roots via `QUANT_DATA_ROOT` / `QUANT_ARTIFACT_ROOT`  

## Remaining

| Severity | Issue | Recommendation |
|----------|-------|----------------|
| LOW | Compose placeholder password | Local only; never reuse in production deploy |
| LOW | Minimal dotenv parser | Acceptable; add python-dotenv only if needed |
