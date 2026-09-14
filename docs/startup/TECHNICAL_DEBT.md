# Technical Debt Register

Audit date: 2026-09-13 (Prompt 1)  
Prompt 2 update: 2026-09-13  
Prompt 3 update: 2026-09-13  

IDs are stable. Do not delete historical entries.

| ID | Severity | Area | Description | Evidence | Impact | Recommended fix | Target phase | Prompt 2 | Prompt 3 |
|----|----------|------|-------------|----------|--------|-----------------|--------------|----------|----------|
| TD-001 | HIGH | Market data | Unadjusted Yahoo OHLCV by default | `ml/data/yahoo.py` `auto_adjust=False` | Distorted returns around corporate actions | Add adjustment policy + provenance field | 2–3 | DEFERRED | DEFERRED |
| TD-002 | HIGH | Market data | Survivorship / static universe | `ml/research/universe.py` | Overstated robustness | PIT universe or explicit bias docs in every report | 2, 10 | DEFERRED | DEFERRED |
| TD-003 | HIGH | ML validation | Chronological split lacks purge | `ml/splitting.py` | Label-boundary leakage for horizon>1 | Purge/embargo helper for single splits | 3 | DEFERRED | DEFERRED |
| TD-004 | HIGH | Backtesting | Multi-horizon economics unsupported | `execution.py` hard fail | Incomplete strategy evaluation | Design multi-horizon model | 3, 9 | DEFERRED | DEFERRED |
| TD-005 | MEDIUM | Research config | Horizon vs WF forecast_horizon desync | `ml/research/config.py` | Methodological mismatch | Enforce equality | 3 | DEFERRED | DEFERRED |
| TD-006 | MEDIUM | Provenance | Experiments lack full artifact contract | DB vs provenance doc | Unreproducible claims | Extend schema | 2, 4 | DEFERRED | DEFERRED |
| TD-007 | MEDIUM | Model lifecycle | Catalog `trained=False` hardcoded | `services/models.py` | UI not artifact-backed | Registry | 4 | DEFERRED | DEFERRED |
| TD-008 | MEDIUM | Frontend | Cumulative chart vs analysis divergence | market page | Confusion | Chart from analysis payload | 1–2 | DEFERRED | DEFERRED |
| TD-009 | MEDIUM | Dependencies | Unpinned Docker requirements | `requirements-docker.txt` | Image drift | Pin ranges | 3 | **RESOLVED** | — |
| TD-010 | MEDIUM | DX | Frontend tests fail on Node 18 | Vitest ESM | Friction | engines/nvmrc | 1 | **RESOLVED** | — |
| TD-011 | MEDIUM | Security | No authentication on API | open routers | Exposure | Authn/z | 12, 14 | DEFERRED | DEFERRED |
| TD-012 | MEDIUM | Jobs | No worker system | sync/offline | Timeouts | Job queue | 13 | DEFERRED | DEFERRED |
| TD-013 | LOW | Data validation | No high≥low checks | `validation.py` | Bad ticks | Expand validators | 3 | DEFERRED | DEFERRED |
| TD-014 | LOW | Backtesting | Default zero costs | `BacktestConfig` | Optimistic nets | Safer defaults | 3 | DEFERRED | DEFERRED |
| TD-015 | LOW | Features | Absolute SMA/EMA levels | feature modules | Nonstationarity | Prefer ratios | 3 | DEFERRED | DEFERRED |
| TD-016 | LOW | Observability | No metrics/tracing | logging only | Ops gap | OTEL later | 8, 15 | DEFERRED | DEFERRED (logging config foundation only) |
| TD-017 | LOW | Docs/product | Legacy vs startup roadmap confusion | README | Confusion | Clarified | 1 | **RESOLVED** | — |
| TD-018 | LOW | API/UI | Unused prediction/POST backtest UI | contracts | Perception | Wire later | 7 | **REDUCED** | DEFERRED |
| TD-019 | LOW | Cache | Process-local TTL only | `core/cache.py` | Multi-worker drift | Redis later | 14 | DEFERRED | DEFERRED |
| TD-020 | MEDIUM | Empirics | Final research report empty | report doc | No attested narrative | Run experiment | 2 | DEFERRED | DEFERRED |
| TD-021 | LOW | Structure | Split drawdown/Sharpe defs | analysis vs backtest | Drift risk | Risk domain | 9 | **NEW** | DEFERRED |
| TD-022 | LOW | Time | Naive calendar dates | provider/API | Timezone risk | Market calendar | 11 | **NEW** | DEFERRED |
| TD-023 | LOW | Symbols | HTTP rejects `^INDEX` | security allow-list | API gap | Quote-path design | 7/11 | **NEW** | DEFERRED |
| TD-024 | LOW | DX | Remaining symbol normalize call sites | repositories | Duplication | Migrate | 3–4 | **NEW** | DEFERRED |
| TD-025 | LOW | Config | Compose still uses well-known placeholder DB password | `docker-compose.yml` | Fine locally; unsafe if copied to prod | Keep documented; forbid in deploy | 14 | — | **NEW** (accepted for local only) |
| TD-026 | LOW | Config | Minimal dotenv parser (no multiline) | `config.maybe_load_dotenv` | Rare .env edge cases | Optional python-dotenv later if needed | 3–8 | — | **NEW** |

---

## Prompt 3 configuration outcomes

- **RESOLVED:** fragmented settings ownership (single `backend.app.core.config`), missing fail-fast CORS/log/path validation, missing safe diagnostics, missing test DB isolation guardrails, missing config contract docs  
- **REDUCED:** TD-016 (log level now configurable; full observability still deferred)  
- **DEFERRED:** methodology and product debts above  

## Priority order (nearest)

1. TD-020 + TD-006 reproducibility  
2. TD-001/TD-003/TD-005 methodology hardening  
3. TD-007 registry  
4. TD-011/TD-012 before public deploy  
