# Persistence Architecture

**Status:** CURRENT foundation  
**Stack:** SQLAlchemy 2.x + Alembic + PostgreSQL (SQLite acceptable for unit tests only)

## Ownership

| Concern | Location |
|---------|----------|
| ORM models | `backend/app/db/models/` |
| Session / engine | `backend/app/db/session.py` |
| Repositories | `backend/app/repositories/` |
| Migrations | `alembic/versions/` |
| Research engine | `ml/` — **no SQLAlchemy sessions** |

## Boundary rules

1. `ml/` must not import `backend.app.db` or SQLAlchemy session objects.  
2. Application services orchestrate: domain compute → map to ORM → repository write.  
3. Do not pass ORM entities into feature engineering, model training, or metric formulas.  
4. Artifact binaries (checkpoints, reports) live on filesystem paths referenced by metadata columns — not as opaque blobs in Postgres for this modular monolith (object storage is FUTURE).

## CURRENT persisted research entities

- `experiments` (+ metrics)  
- `walk_forward_runs` / `walk_forward_folds`  
- `out_of_sample_predictions`  
- `backtest_runs` / metrics / equity points  

## Known gaps (tracked)

- TD-006: incomplete dataset/feature/code-revision provenance columns  
- TD-007: model registry not yet first-class  
- No news/NLP/portfolio/user tables until those domains are implemented
