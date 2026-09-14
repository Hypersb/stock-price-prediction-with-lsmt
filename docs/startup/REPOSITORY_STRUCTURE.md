# Repository Structure

Audit date: 2026-09-13 (Prompt 2)  
Purpose: canonical map of ownership so future phases do not invent competing layouts.

---

## Top-level directories

| Path | Responsibility | Owner |
|------|----------------|-------|
| `backend/` | FastAPI app, HTTP routes, services, schemas, DB session/models, repositories | Application + infrastructure |
| `ml/` | Quantitative/ML research domain library (no FastAPI/UI imports) | Domain |
| `frontend/` | Next.js research dashboard | Presentation |
| `alembic/` | Database migrations | Infrastructure |
| `tests/` | Python automated tests | Quality |
| `scripts/` | Developer/ops CLI entry points | Tooling |
| `docs/` | Product, architecture, methodology, ADRs, startup audits | Documentation |
| `data/` | Local research extracts (`raw/`, `processed/`) — generated, gitignored contents | Runtime / research local |
| `notebooks/` | Exploratory Jupyter notebooks | Research (non-CI) |
| `.github/workflows/` | CI | Tooling |

---

## Layer model (mapped to this repo)

```text
Presentation     → frontend/
Application      → backend/app/api/, backend/app/services/, backend/app/dependencies.py
Domain           → ml/  (+ backend/app/schemas as API DTOs, not domain math)
Infrastructure   → backend/app/db/, backend/app/core/{cache,config,logging,security},
                   ml/data/{yahoo,storage}, alembic/, scripts/
```

### Dependency direction

```text
frontend  →  HTTP JSON only (no Python imports)
backend.api  →  backend.services  →  ml.*  and/or  backend.repositories → DB
ml.*  ↛  backend.*
ml.*  ↛  frontend.*
```

Protected by `tests/test_architecture_boundaries.py`.

---

## Important entry points

See [`ENTRY_POINTS.md`](ENTRY_POINTS.md).

---

## Runtime-owned vs research-owned

| Kind | Paths |
|------|-------|
| Runtime API | `backend/`, `alembic/`, Docker Compose services |
| Research domain | `ml/`, `notebooks/`, `docs/research-methodology.md`, `docs/final-research-report.md` |
| Product UI | `frontend/` |
| Local generated | `data/raw/*`, `data/processed/*`, `artifacts/`, `checkpoints/`, `*.pt`, `.next/`, caches |
| Secrets / local env | `.env`, `frontend/.env.local` (gitignored) |

---

## Ambiguities / deferred moves

| Item | Assessment | Action in Prompt 2 |
|------|------------|--------------------|
| Drawdown in `ml/analysis` vs `ml/backtesting/metrics` | Different inputs (returns vs equity path); related but not identical | **DEFER** consolidation (TD risk domain) |
| Symbol `.strip().upper()` in many call sites | Same semantics | Centralize **canonical** helper in `ml/data/symbols.py`; migrate primary request/security paths |
| `backend/app/core/json_utils.py` | API serialization helper, not dumping ground | Keep |
| Empty `frontend/types/index.ts` | Unused barrel | Document; leave (no UI redesign) |
| Prediction GET / POST backtests unused by UI | Planned API surface | Keep; document FUTURE-PLANNED |
| `scripts/fetch_market_data.py` `sys.path` hack | Fragile | Prefer `python -m scripts.fetch_market_data` |

---

## Generated artifacts policy

| Class | Examples | VCS |
|-------|----------|-----|
| SOURCE | `ml/`, `backend/`, `frontend/app/` | Tracked |
| FIXTURE | Synthetic frames inside tests | Tracked |
| GENERATED | `data/raw/*.csv`, checkpoints, `.next`, coverage | Ignored |
| LOCAL | `.venv`, `node_modules`, `.env` | Ignored |
| SECRET | API keys, DB passwords | Never commit |

---

## Naming

- Repo name retains historical `lsmt` spelling; product docs may say “Fold”.  
- Prefer domain folders under `ml/` over generic `utils/`.  
- No new catch-all `helpers.py` introduced in Prompt 2.

---

## Symbol normalization contract

| Layer | Behavior |
|-------|----------|
| Research identity | `ml.data.symbols.normalize_symbol` → strip + uppercase; preserve `.` `-` `^` |
| HTTP path safety | `validate_ticker_symbol` = normalize + allow-list `[A-Z][A-Z0-9.\-]{0,15}` |
| CSV filenames | `HistoricalDataStore` may further sanitize unsafe filesystem characters |
| Frontend | Passes symbols through URL/query; relies on API validation |

`^GSPC`-style indices are valid research symbols but currently rejected by the HTTP allow-list (documented limitation).

---

## Time / date consistency (audit notes)

| Area | Current behavior | Prompt 2 action |
|------|------------------|-----------------|
| Market bars | Provider dates normalized to calendar `date` via pandas | Keep |
| API JSON | `to_iso_date` emits ISO calendar dates | Keep |
| DB timestamps | SQLAlchemy models use date/datetime fields per schema | No change |
| Timezones | Largely **naive / exchange-local calendar dates** for EOD research | **DEFER** full market-calendar design |
| Frontend | ISO date strings in query params | Keep |

No silent timezone conversions were introduced in Prompt 2.
