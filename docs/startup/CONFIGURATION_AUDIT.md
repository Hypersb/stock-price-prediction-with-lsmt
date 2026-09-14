# Configuration & Secret Audit

Audit date: 2026-09-13  
Policy: **do not print secret values**. If a secret appears committed, report file/pattern only.

---

## Configuration sources

| Source | Role |
|--------|------|
| `.env.example` | Documented placeholders for backend/frontend |
| `.env` (local) | Present on disk; **gitignored** — not tracked |
| `frontend/.env.example` | `NEXT_PUBLIC_API_BASE_URL` |
| `frontend/.env.local` | Local public API URL; **gitignored** via frontend `.env*` rule |
| `backend/app/core/config.py` | `Settings` loaded from environment |
| `frontend/lib/env.ts` | Public API base URL + defaults |
| `docker-compose.yml` | Dev service env (placeholder DB creds) |
| `alembic.ini` / `alembic/env.py` | Migrations; DB URL from env |
| CI workflow env | `APP_ENV=test`, ephemeral Postgres creds |

---

## Secret handling verification

| Check | Result |
|-------|--------|
| `.env` tracked by git? | **No** (`git check-ignore` → `.gitignore`; `git ls-files` has no `.env`) |
| `frontend/.env.local` tracked? | **No** |
| Real API keys found committed? | **No** — `MARKET_DATA_API_KEY` empty in examples |
| Dev passwords in examples/compose? | Placeholder `user` / `password` documented as non-production |

**No committed production secrets identified.**  
Do not commit `.env` in future prompts.

---

## Hardcoded / environment-specific settings

| Item | Where | Notes |
|------|-------|-------|
| Default CORS localhost | `Settings` | Dev-oriented |
| Default page sizes / max rows | `Settings` + `.env.example` | Safety limits |
| Market cache TTL 60s / size 64 | `Settings` | Process-local |
| Model catalog entries | `backend/app/services/models.py` | Hardcoded metadata |
| Default symbol `AAPL` | `frontend/lib/env.ts` | UI default |
| Default date range ~1y | `frontend/lib/format.ts` | UI default |
| Compose DB URL/password | `docker-compose.yml` | Dev placeholders |
| App title/version strings | `main.py`, settings | Non-secret |

---

## Model / research parameters

Typically code defaults in:

- `ml/training/config.py`  
- `ml/validation/config.py`  
- `ml/backtesting/config.py`  
- `ml/research/config.py`  
- `ml/neural/config.py`  

These are research configuration, not secrets. Future: move critical run params into provenance records.

---

## Provider settings

- Yahoo via yfinance; optional `MARKET_DATA_API_KEY` reserved for future providers  
- Never expose provider keys through `NEXT_PUBLIC_*` (documented and tested)

---

## Risks / recommendations

| Severity | Issue | Recommendation |
|----------|-------|----------------|
| MEDIUM | Compose/dev passwords are well-known placeholders | Fine for local; forbid in prod deploy docs |
| MEDIUM | `requirements-docker.txt` unpinned | Pin in config architecture prompt |
| LOW | Settings use `os.getenv` + dataclass rather than pydantic-settings | Acceptable; standardize later |
| LOW | Frontend default symbol/date are hardcoded | Keep as UX defaults |

---

## Redaction rules going forward

1. Never log `DATABASE_URL` password or `MARKET_DATA_API_KEY`  
2. Existing middleware redacts Authorization/Cookie/API-key headers  
3. Health/ready payloads must not include secrets (covered by tests)  
