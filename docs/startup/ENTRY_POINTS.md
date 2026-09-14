# Entry Points

Audit date: 2026-09-13 (Prompt 2)

Classification: **production** (container/API runtime), **research** (offline science), **development** (local DX).

---

## HTTP / applications

| Name | Command | Purpose | Inputs | Outputs | Dependencies | Class |
|------|---------|---------|--------|---------|--------------|-------|
| FastAPI app | `uvicorn backend.app.main:app --reload` | Research API | HTTP, env | JSON | `backend`, `ml`, optional Postgres | production / development |
| Docker API entry | `python scripts/docker_backend_entrypoint.py` | Migrate then serve | Env `DATABASE_URL`, ports | HTTP on 8000 | Alembic, uvicorn | production (Compose) |
| Next.js dev | `cd frontend && npm run dev` | Dashboard | Env `NEXT_PUBLIC_API_BASE_URL` | UI :3000 | Node 20+ | development |
| Next.js prod | `cd frontend && npm run build && npm start` | Production UI | Same | UI | Node 20+ | production |

---

## Database

| Name | Command | Purpose | Inputs | Outputs | Dependencies | Class |
|------|---------|---------|--------|---------|--------------|-------|
| Alembic upgrade | `alembic upgrade head` | Apply migrations | `DATABASE_URL` | Schema | Alembic, Postgres | production / development |
| Alembic revision | `alembic revision --autogenerate -m "..."` | Create migration | Models | Script under `alembic/versions/` | Dev only | development |

---

## Market data / research CLI

| Name | Command | Purpose | Inputs | Outputs | Dependencies | Class |
|------|---------|---------|--------|---------|--------------|-------|
| Fetch OHLCV | `PYTHONPATH=. python -m scripts.fetch_market_data SYMBOL START END [--save]` | Ingest Yahoo history | Symbol, dates | stdout; optional `data/raw/` | yfinance, `ml.data` | research / development |
| Final research pipeline | Python API: `ml.research.pipeline.run_final_research_evaluation` | Offline multi-model evaluation | Market frames + config | `FinalResearchResult` | `ml` | research |
| Report render | `ml.research.report.render_final_research_report` | Markdown report | Result or `None` | Markdown (empty if None) | `ml.research` | research |
| Notebooks | `jupyter notebook` / lab under `notebooks/` | Exploration | Manual | Notebook outputs (local) | jupyter | research |

There is **no** dedicated CLI for walk-forward or backtests beyond Python APIs and HTTP `POST /api/v1/backtests`.

---

## Quality / health

| Name | Command | Purpose | Class |
|------|---------|---------|-------|
| Pytest | `APP_ENV=test PYTHONPATH=. pytest -q` | Python tests | development |
| Ruff | `ruff check backend tests ml scripts` | Lint | development |
| Frontend test | `cd frontend && npm test` | Vitest | development |
| Repo health | `PYTHONPATH=. python -m scripts.check_repo_health` | Structural invariants | development |
| Compose stack | `docker compose up --build` | Full local stack | development |

---

## Obsolete / duplicated

| Item | Status |
|------|--------|
| `sys.path.insert` in fetch script | **Removed** in Prompt 2 in favor of `-m scripts...` |
| Competing Make/npm task runners | None previously; light `Makefile` added as thin wrappers only |
| Duplicate FastAPI factories | Single `create_app` in `backend.app.main` |

---

## Intentionally kept unused-by-UI APIs

| Endpoint | Status |
|----------|--------|
| `GET /api/v1/ready` | Client helper exists; pages unused — **FUTURE-PLANNED / ops** |
| `GET /api/v1/models/{model}/predictions/{symbol}` | API-only OOS reads — **FUTURE-PLANNED UI** |
| `POST /api/v1/backtests` | On-demand backtest — **FUTURE-PLANNED UI** |
