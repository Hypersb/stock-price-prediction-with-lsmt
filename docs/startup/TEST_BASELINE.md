# Test Baseline

Baseline date: 2026-09-13  
Purpose: freeze the quality gate against which later Phase 1–15 work is measured.  
Do not weaken tests to force green.

---

## Commands

### Python

```bash
# from repo root, Python 3.12 venv
export PYTHONPATH=.
export APP_ENV=test
ruff check backend tests ml
pytest -q
```

Optional Postgres-backed subset (CI `database` job):

```bash
export DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/quant_research
alembic upgrade head
pytest -q tests/test_db_migrations.py tests/test_db_session.py \
  tests/test_db_repositories.py tests/test_api_persistence.py \
  tests/test_api_ready.py tests/test_research_persistence.py \
  tests/test_fullstack_integration.py
```

### Frontend

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

**Node requirement:** Vitest failed on Node **v18.20.8** (`ERR_REQUIRE_ESM` loading Vite).  
Same suite passed on Node **v20.20.2**. CI uses Node **22**. Treat **Node ≥ 20** as required for frontend tests.

### CI

`.github/workflows/ci.yml` jobs: `backend` (ruff + pytest), `frontend` (lint/typecheck/test/build), `database` (alembic + persistence tests against Postgres 16).

---

## Python results (this audit)

| Metric | Value |
|--------|-------|
| Command | `APP_ENV=test PYTHONPATH=. pytest -q` |
| Collected | 301 |
| Passed | **300** |
| Failed | **0** |
| Skipped | **1** |
| Warnings | **3** |
| Duration | ~24s |

### Skipped

| Test | Reason |
|------|--------|
| `tests/test_postgres_migrations.py` | `postgresql DATABASE_URL required` |

### Warnings

1. Starlette/FastAPI TestClient deprecation (httpx2)
2. `anyio.abc.BlockingPortal` deprecation alias
3. `ml/data/validation.py` date parse inference warning in invalid-date test case

### Ruff

```text
ruff check backend tests ml
All checks passed!
```

---

## Frontend results (this audit)

| Environment | Result |
|-------------|--------|
| Node v18.20.8 | **BROKEN startup** — Vitest config ESM load failure |
| Node v20.20.2 | **14 passed** / 7 files / ~1.1s |

Lint / typecheck / production build were **not** re-run end-to-end in this audit beyond unit tests (CI covers them). Record as **UNKNOWN locally** for lint/typecheck/build until executed; CI config expects them.

---

## Coverage shape (qualitative)

Strong unit coverage for:

- market data normalize/validate/ingest
- features / targets / splits / preprocessing
- baselines, LSTM pieces, walk-forward, backtest math
- API contracts, security headers, persistence models

Weaker / absent:

- notebook execution
- full multi-asset Yahoo live integration (mostly fakes)
- browser E2E
- auth (N/A)
- load/performance

---

## Baseline rules for future prompts

1. Report new failures honestly.
2. Do not delete or skip assertions to hide regressions.
3. Prefer adding tests when changing financial formulas.
4. Frontend contributors must use Node ≥ 20 (prefer 22 to match CI).
5. Postgres migration skip is expected without `DATABASE_URL`; CI database job must stay green.
