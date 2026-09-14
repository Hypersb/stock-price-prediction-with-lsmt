# Technical Debt Register

Audit date: 2026-09-13  
IDs are stable references for later phases. This prompt documents; it does not fix broadly.

| ID | Severity | Area | Description | Evidence | Impact | Recommended fix | Target phase |
|----|----------|------|-------------|----------|--------|-----------------|--------------|
| TD-001 | HIGH | Market data | Unadjusted Yahoo OHLCV by default | `ml/data/yahoo.py` `auto_adjust=False` | Distorted returns around corporate actions | Add adjustment policy + provenance field | 2–3 |
| TD-002 | HIGH | Market data | Survivorship / static universe | `ml/research/universe.py` | Overstated robustness | PIT universe or explicit bias docs in every report | 2, 10 |
| TD-003 | HIGH | ML validation | Chronological split lacks purge | `ml/splitting.py` used without purge in diagnostics | Label-boundary leakage for horizon>1 | Purge/embargo helper for single splits | 3 |
| TD-004 | HIGH | Backtesting | Multi-horizon economics unsupported | `execution.py` hard fail | Incomplete strategy evaluation | Design non-overlapping / holding-period model | 3, 9 |
| TD-005 | MEDIUM | Research config | Horizon vs WF forecast_horizon desync possible | `ml/research/config.py` | Silent methodological mismatch | Enforce equality in config validation | 3 |
| TD-006 | MEDIUM | Provenance | Experiments lack full artifact contract | DB models vs `ARTIFACT_PROVENANCE.md` | Unreproducible claims risk | Extend schema + writers | 2, 4 |
| TD-007 | MEDIUM | Model lifecycle | Catalog `trained=False` hardcoded | `services/models.py` | UI cannot reflect real artifacts | Registry-backed catalog | 4 |
| TD-008 | MEDIUM | Frontend | Cumulative chart vs analysis metric divergence under pagination | `frontend/app/market/page.tsx` | User confusion | Chart from analysis payload or full series | 1–2 |
| TD-009 | MEDIUM | Dependencies | Unpinned Docker requirements | `requirements-docker.txt` | Image drift | Pin to runtime set | 3 |
| TD-010 | MEDIUM | DX | Frontend tests fail on Node 18 | Vitest/Vite ESM error | Contributor friction | Document/engines field Node ≥20 | 1 |
| TD-011 | MEDIUM | Security | No authentication on API | routers open | Unsafe exposure if publicly deployed | Authn/z in user platform phase | 12, 14 |
| TD-012 | MEDIUM | Jobs | Long research runs are sync/offline only | no worker system | Timeouts / poor UX | Job queue + status API | 13 |
| TD-013 | LOW | Data validation | No high≥low style checks | `validation.py` | Bad ticks accepted | Expand validators | 3 |
| TD-014 | LOW | Backtesting | Default zero costs | `BacktestConfig` | Optimistic nets | Safer research defaults + UI warnings | 3 |
| TD-015 | LOW | Features | Absolute SMA/EMA levels | feature modules | Nonstationarity | Prefer ratio features in defaults | 3 |
| TD-016 | LOW | Observability | No metrics/tracing backend | logging only | Hard to operate | OTEL/metrics in launch phase | 8, 15 |
| TD-017 | LOW | Docs/product | Prior “15 phases complete” vs new 15-phase startup roadmap | README / project-status | Confusion | Clarify legacy vs startup phases in README | 1 |
| TD-018 | LOW | API/UI | Prediction GET + POST backtests unused by UI | contracts/pages | Dead surface area perception | Wire or document as API-only | 7 |
| TD-019 | LOW | Cache | Process-local TTL only | `core/cache.py` | Incorrect under multi-worker without sticky assumptions | Redis when scaling out | 14 |
| TD-020 | MEDIUM | Empirics | Final research report empty | `docs/final-research-report.md` | No attested performance narrative | Run provenance-backed experiment | 2 |

---

## Priority order (nearest)

1. TD-017/TD-010 documentation clarity (Phase 1)  
2. TD-020 + TD-006 reproducibility (Phase 2)  
3. TD-001/TD-003/TD-005 methodology hardening (Phase 3)  
4. TD-007 registry (Phase 4)  
5. TD-011/TD-012 before any public deploy  
