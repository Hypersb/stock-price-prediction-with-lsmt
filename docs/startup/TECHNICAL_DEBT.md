# Technical Debt Register

Audit date: 2026-09-13 (Prompt 1)  
Prompt 2 update: 2026-09-13  

IDs are stable. Do not delete historical entries.

Status legend for Prompt 2 column: **RESOLVED** / **REDUCED** / **DEFERRED** / **NEW** / unchanged blank.

| ID | Severity | Area | Description | Evidence | Impact | Recommended fix | Target phase | Prompt 2 |
|----|----------|------|-------------|----------|--------|-----------------|--------------|----------|
| TD-001 | HIGH | Market data | Unadjusted Yahoo OHLCV by default | `ml/data/yahoo.py` `auto_adjust=False` | Distorted returns around corporate actions | Add adjustment policy + provenance field | 2–3 | DEFERRED |
| TD-002 | HIGH | Market data | Survivorship / static universe | `ml/research/universe.py` | Overstated robustness | PIT universe or explicit bias docs in every report | 2, 10 | DEFERRED |
| TD-003 | HIGH | ML validation | Chronological split lacks purge | `ml/splitting.py` used without purge in diagnostics | Label-boundary leakage for horizon>1 | Purge/embargo helper for single splits | 3 | DEFERRED |
| TD-004 | HIGH | Backtesting | Multi-horizon economics unsupported | `execution.py` hard fail | Incomplete strategy evaluation | Design non-overlapping / holding-period model | 3, 9 | DEFERRED |
| TD-005 | MEDIUM | Research config | Horizon vs WF forecast_horizon desync possible | `ml/research/config.py` | Silent methodological mismatch | Enforce equality in config validation | 3 | DEFERRED |
| TD-006 | MEDIUM | Provenance | Experiments lack full artifact contract | DB models vs `ARTIFACT_PROVENANCE.md` | Unreproducible claims risk | Extend schema + writers | 2, 4 | DEFERRED |
| TD-007 | MEDIUM | Model lifecycle | Catalog `trained=False` hardcoded | `services/models.py` | UI cannot reflect real artifacts | Registry-backed catalog | 4 | DEFERRED |
| TD-008 | MEDIUM | Frontend | Cumulative chart vs analysis metric divergence under pagination | `frontend/app/market/page.tsx` | User confusion | Chart from analysis payload or full series | 1–2 | DEFERRED |
| TD-009 | MEDIUM | Dependencies | Unpinned Docker requirements | `requirements-docker.txt` | Image drift | Pin to runtime set | 3 | **RESOLVED** (compatible-release pins aligned with `requirements.txt`) |
| TD-010 | MEDIUM | DX | Frontend tests fail on Node 18 | Vitest/Vite ESM error | Contributor friction | Document/engines field Node ≥20 | 1 | **RESOLVED** (`engines`, `.nvmrc`, docs) |
| TD-011 | MEDIUM | Security | No authentication on API | routers open | Unsafe exposure if publicly deployed | Authn/z in user platform phase | 12, 14 | DEFERRED |
| TD-012 | MEDIUM | Jobs | Long research runs are sync/offline only | no worker system | Timeouts / poor UX | Job queue + status API | 13 | DEFERRED |
| TD-013 | LOW | Data validation | No high≥low style checks | `validation.py` | Bad ticks accepted | Expand validators | 3 | DEFERRED |
| TD-014 | LOW | Backtesting | Default zero costs | `BacktestConfig` | Optimistic nets | Safer research defaults + UI warnings | 3 | DEFERRED |
| TD-015 | LOW | Features | Absolute SMA/EMA levels | feature modules | Nonstationarity | Prefer ratio features in defaults | 3 | DEFERRED |
| TD-016 | LOW | Observability | No metrics/tracing backend | logging only | Hard to operate | OTEL/metrics in launch phase | 8, 15 | DEFERRED |
| TD-017 | LOW | Docs/product | Prior “15 phases complete” vs new 15-phase startup roadmap | README / project-status | Confusion | Clarify legacy vs startup phases in README | 1 | **RESOLVED** (Prompt 1) |
| TD-018 | LOW | API/UI | Prediction GET + POST backtests unused by UI | contracts/pages | Dead surface area perception | Wire or document as API-only | 7 | **REDUCED** (documented FUTURE-PLANNED in `ENTRY_POINTS.md`; not removed) |
| TD-019 | LOW | Cache | Process-local TTL only | `core/cache.py` | Incorrect under multi-worker without sticky assumptions | Redis when scaling out | 14 | DEFERRED |
| TD-020 | MEDIUM | Empirics | Final research report empty | `docs/final-research-report.md` | No attested performance narrative | Run provenance-backed experiment | 2 | DEFERRED |
| TD-021 | LOW | Structure | Drawdown/Sharpe definitions split across analysis vs backtesting metrics | `ml/analysis/drawdown.py`, `ml/backtesting/metrics.py` | Future drift risk | Consolidate under risk domain carefully | 9 | **NEW** (documented; not merged) |
| TD-022 | LOW | Time | Naive calendar dates; no exchange calendar service | provider/API/DB | Intraday/timezone product risk later | Market-calendar architecture | 11 | **NEW** |
| TD-023 | LOW | Symbols | HTTP allow-list rejects `^INDEX` style symbols | `validate_ticker_symbol` | Cannot query some Yahoo indices via API | Dedicated quote-path design | 7 / 11 | **NEW** |
| TD-024 | LOW | DX | Remaining `.strip().upper()` call sites outside canonical helper | repositories, research modules | Mild duplication | Migrate call sites opportunistically | 3–4 | **NEW** (REDUCED overall via `ml.data.symbols`) |

---

## Priority order (nearest)

1. TD-020 + TD-006 reproducibility (Phase 2 empirics)  
2. TD-001/TD-003/TD-005 methodology hardening (Phase 3)  
3. TD-007 registry (Phase 4)  
4. TD-011/TD-012 before any public deploy  
