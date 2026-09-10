# Database Persistence

Phase 12 adds a PostgreSQL-oriented persistence layer for quantitative research metadata and results.

## Architecture

```text
FastAPI routes
    ↓
Pydantic response schemas
    ↓
repositories
    ↓
SQLAlchemy 2.x ORM
    ↓
PostgreSQL
```

ORM models are not used as public API contracts. Routes depend on repositories and return Pydantic schemas.

## PostgreSQL Requirement

The production-oriented database is PostgreSQL with the `psycopg` (v3) driver:

```text
postgresql+psycopg://user:password@localhost:5432/quant_research
```

Unit tests may use isolated temporary SQLite databases for offline determinism. SQLite does not prove every PostgreSQL behavior.

## SQLAlchemy

- Declarative base: `backend.app.db.base.Base`
- Engine/session helpers: `backend.app.db.session`
- Engine creation is explicit (`configure_database` / `build_database`), not an import-time side effect
- UUID primary keys are used consistently
- JSON columns store flexible configuration and fold metrics
- Non-finite metric values are normalized to `NULL` before persistence

## Alembic

Configuration:

- `alembic.ini`
- `alembic/env.py` (reads `DATABASE_URL`)
- Initial revision: `alembic/versions/8190595e3b16_initial_research_persistence_schema.py`

Commands (from repository root, with `DATABASE_URL` set):

```powershell
$env:DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/quant_research"
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic downgrade -1
```

## Environment Configuration

`.env.example` includes:

```text
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/quant_research
```

Never commit a real `.env` or password.

## Local Development

1. Start PostgreSQL (local install or Docker Compose below).
2. Set `DATABASE_URL`.
3. Run migrations: `alembic upgrade head`
4. Start API: `uvicorn backend.app.main:app --reload`

### Optional Docker Compose

```powershell
docker compose up -d postgres
```

This starts only PostgreSQL on port `5432` with placeholder credentials matching `.env.example`.

## Schema Overview

| Table | Purpose |
|-------|---------|
| `experiments` | Model/training experiment metadata and checkpoint references |
| `experiment_metrics` | Split/metric_name/value rows for experiments |
| `walk_forward_runs` | Walk-forward campaign configuration |
| `walk_forward_folds` | Per-fold windows, counts, and fold metrics |
| `out_of_sample_predictions` | Chronological OOS prediction observations |
| `backtest_runs` | Backtest configuration and summary |
| `backtest_metrics` | Flexible backtest metric rows |
| `backtest_equity_points` | Date/position/return/equity series |

## Important Relationships

- experiment → metrics (CASCADE delete)
- experiment → walk_forward_runs (SET NULL)
- walk_forward_run → folds (CASCADE)
- walk_forward_run / experiment → out_of_sample_predictions
- experiment / walk_forward_run → backtest_runs (SET NULL)
- backtest_run → metrics / equity_points (CASCADE)

## Indexes

Indexes exist for common access patterns:

- experiments: `symbol`, `model_name`
- experiment_metrics: `experiment_id`
- walk_forward_runs: `experiment_id`, `symbol`
- walk_forward_folds: `run_id`
- out_of_sample_predictions: `symbol`, `prediction_date`, `experiment_id`, `walk_forward_run_id`
- backtest_runs: `symbol`, `experiment_id`, `walk_forward_run_id`
- backtest_metrics / equity_points: `backtest_id`

## Persistent API Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v1/experiments` |
| GET | `/api/v1/experiments/{experiment_id}` |
| GET | `/api/v1/experiments/{experiment_id}/metrics` |
| GET | `/api/v1/walk-forward/{run_id}` |
| GET | `/api/v1/backtests` |
| GET | `/api/v1/backtests/{backtest_id}` |

List endpoints support `limit` / `offset` pagination with safe maximums.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check backend tests alembic
```

Database tests use temporary SQLite files or in-memory databases. They never target a developer’s real PostgreSQL database unless `DATABASE_URL` is explicitly pointed there for manual migration checks.

## Limitations

- No authentication or multi-user tenancy
- No storage of PyTorch weight blobs in PostgreSQL
- No Celery/Redis job queue for training
- Synchronous backtest POST still accepts explicit OOS payloads; persistence APIs currently expose stored results
- SQLite tests are compatibility aids, not a substitute for PostgreSQL validation in deployment
