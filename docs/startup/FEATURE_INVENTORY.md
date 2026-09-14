# Feature Inventory

Audit date: 2026-09-13  
Method: code inspection + test execution. Classifications are behavioral, not filename-based.

Legend:

| Status | Meaning |
|--------|---------|
| IMPLEMENTED | Verified working path with meaningful tests or clear runtime behavior |
| PARTIAL | Exists but incomplete, constrained, or not production-hardened |
| PLACEHOLDER | Present as stub, template, decorative UI, or awaiting real data |
| BROKEN | Present but fails under normal expected use |
| NOT IMPLEMENTED | No meaningful implementation |
| UNKNOWN | Could not verify in this audit |

Production-ready means safe for multi-user production SaaS without major hardening. Almost nothing here meets that bar yet; research-local use is separate.

---

## Market data

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Provider abstraction | IMPLEMENTED | `ml/data/` | `provider.py`, `yahoo.py` | `MarketDataProvider` interface; Yahoo implementation | `test_market_data_provider.py`, `test_yahoo_provider.py` | yfinance | Single provider | No | Keep; add licensed providers later |
| Historical OHLCV ingest | IMPLEMENTED | `ml/data/` | `ingestion.py`, `requests.py`, `normalize.py`, `validation.py` | Request validate → fetch → normalize → validate → optional CSV | Many `test_market_data_*` | pandas, yfinance | Unadjusted closes (`auto_adjust=False`) | No | Option for adjusted prices |
| Local CSV persistence | IMPLEMENTED | `ml/data/`, `data/raw/` | `storage.py` | Writes validated frames under `data/raw` | `test_market_data_storage.py` | pandas | Not a warehouse; gitignored artifacts | No | Keep for research extracts |
| Near-real-time / streaming | NOT IMPLEMENTED | — | — | No websocket/stream feed | — | — | Historical only | No | Phase 11 |
| Multi-provider failover | NOT IMPLEMENTED | — | — | Yahoo only | — | — | Single source | No | Later |

## Quantitative analysis / EDA

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Returns / vol / drawdown / correlation | IMPLEMENTED | `ml/analysis/` | `returns.py`, `volatility.py`, `drawdown.py`, `correlation.py`, `statistics.py`, `rolling.py`, `cumulative.py` | Library metrics over series | Matching `tests/test_*` | pandas, numpy | Research library, not portfolio engine | No | Keep; add formal annualization contract docs |
| Market analysis API | IMPLEMENTED | `backend/app/` | `services/analysis.py`, `api/v1/analysis.py` | On-demand stats from Yahoo series | `test_api_analysis.py` | ml.analysis | Depends on Yahoo availability | No | Cache carefully; document freshness |
| Notebooks EDA | PARTIAL | `notebooks/` | `01_*.ipynb` … `09_*.ipynb` | Exploratory notebooks exist | Untested as notebooks | jupyter | Not CI-gated | No | Treat as examples only |

## Feature engineering

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Feature pipeline | IMPLEMENTED | `ml/features/` | `pipeline.py`, lag/momentum/trend/ema/volatility/volume/indicators | Builds leakage-oriented trailing features | Extensive feature tests | pandas | Absolute SMA/EMA levels non-stationary | No | Prefer return/ratio features for research defaults |
| Feature validation | IMPLEMENTED | `ml/features/validation.py` | Forbidden future/target column names | `test_feature_validation.py` | — | Name heuristics only | No | Strengthen schema contracts |
| Features API | IMPLEMENTED | `backend` + `frontend` | `services/features.py`, `app/features/page.tsx` | On-demand features for symbol/range | `test_api_features.py` | ml.features | Paginated; not persisted feature store | No | Feature store / versioning (Phase 3–4) |

## Targets / supervised datasets

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Future-return targets | IMPLEMENTED | `ml/targets/returns.py` | `shift(-horizon)` future returns | `test_future_return_targets.py` | pandas | Correct by construction | No | Keep |
| Direction targets | IMPLEMENTED | `ml/targets/direction.py` | Up iff return > 0; NA preserved | `test_direction_targets.py` | — | Flats → class 0 | No | Keep documented semantics |
| Dataset assembly / boundaries | IMPLEMENTED | `ml/dataset.py`, `ml/boundaries.py` | Drops incomplete rows; excludes targets from X | `test_dataset_assembly.py`, `test_boundaries.py` | — | Warmup loss intentional | No | Keep |

## Preprocessing / splitting

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Train-only scaler | IMPLEMENTED | `ml/preprocessing.py`, `ml/validation/preprocessing.py` | StandardScaler fit on train/fold-train only | `test_preprocessing.py`, `test_fold_preprocessing.py` | sklearn | Features only; targets unscaled | No | Keep |
| Chronological split | IMPLEMENTED | `ml/splitting.py`, `ml/split_validation.py` | Contiguous 70/15/15; no shuffle | `test_splitting.py`, `test_split_validation.py` | — | No purge on single split | No | Add purge/embargo for single splits |
| Prediction inverse transform | NOT IMPLEMENTED | — | — | Not needed for unscaled return targets | — | — | Would be required for scaled price targets | No | Document contract; add if targets change |

## Models

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Naive baselines | IMPLEMENTED | `ml/models/baselines.py` | Persistence / naive direction | naive tests | numpy/pandas | Simple | No | Keep |
| Linear / logistic | IMPLEMENTED | `ml/models/regression.py`, `classification.py` | sklearn wrappers | matching tests | sklearn | Fixed hyperparameters | No | Nested CV later if tuning added |
| Random forest / GB | IMPLEMENTED | `ml/models/ensemble.py`, `boosting.py` | Tabular baselines | matching tests | sklearn | Weak defaults in some WF paths | No | Document capacity choices |
| LSTM regressor/classifier | IMPLEMENTED | `ml/neural/`, `ml/training/` | PyTorch LSTM + trainer, early stop, checkpoints | many neural/training tests | torch | CPU research defaults; no online serving train | No | Harden artifact packaging |
| Model catalog API | PARTIAL | `backend/app/services/models.py` | Hardcoded list; `trained=False` always | `test_api_models.py` | — | Not a registry of artifacts | No | Wire to real registry (Phase 4) |
| Transformers / deep alternatives | NOT IMPLEMENTED | — | — | Explicit future work | — | — | — | No | Later optional |

## Validation / evaluation

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Walk-forward folds + purge | IMPLEMENTED | `ml/validation/` | expanding/rolling, purge, gap, fold preprocess | extensive validation tests | pandas | Default gap=0 | No | Enforce horizon sync |
| Baseline / LSTM WF | IMPLEMENTED | `validation/baselines.py`, `lstm.py` | Retrains per fold; OOS preds | `test_*walk_forward*` | models + neural | Heavy runtime for full research | No | Job queue for long runs |
| Metrics (reg/clf) | IMPLEMENTED | `ml/evaluation/` | MAE/RMSE/dir-acc; clf metrics | matching tests | sklearn/numpy | Dir-acc edge cases | No | Keep |
| Model comparison helpers | IMPLEMENTED | `ml/comparison.py` | Val-set comparison utilities | `test_comparison.py` | — | Not nested CV | No | Keep clear of test-set tuning |

## Backtesting / risk

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Signals + execution align | IMPLEMENTED | `ml/backtesting/signals.py`, `execution.py` | Next-bar align; **horizon=1 only** | execution/signal tests | pandas | Multi-horizon blocked | No | Design multi-horizon carefully |
| Costs / engine / metrics | IMPLEMENTED | `costs.py`, `engine.py`, `metrics.py`, `returns.py` | Turnover bps costs; Sharpe/Sortino/MDD | cost/metrics/engine tests | numpy | Simplified cost model; default 0 cost | No | Richer cost scenarios |
| Fold-aware stitching | IMPLEMENTED | `fold_aware.py` | Rejects overlapping OOS; no gap annualization | `test_fold_aware_backtest.py` | — | Conservative | No | Keep |
| Benchmark compare | IMPLEMENTED | `benchmark.py` | Buy-and-hold on same dates | `test_benchmark.py` | — | Single-asset B&H | No | Keep |
| Risk analytics (standalone engine) | PARTIAL | `ml/risk/` + analysis/backtest | VaR/ES/Calmar/beta + existing Sharpe/DD | `test_risk_metrics.py` | — | Historical VaR; not factor risk | No | Portfolio risk |
| Portfolio analytics | PARTIAL | `ml/portfolio/` | Weights/HHI helpers (no brokerage) | `test_portfolio_analytics.py` | — | Analytical only | No | Persistence + UI |

## Research orchestration / reporting

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Final research pipeline | IMPLEMENTED | `ml/research/pipeline.py` | Multi-asset WF + diagnostics orchestration | `test_final_research_pipeline.py` | many ml modules | Needs operator-supplied data | No | Persist fingerprints (Phase 2) |
| Report renderer | IMPLEMENTED | `ml/research/report.py` | Renders markdown; empty when no result | `test_research_report.py` | — | Does not invent metrics | No | Keep discipline |
| Empirical report doc | IMPLEMENTED | `docs/final-research-report.md` + `docs/research/empirics/` | Experiment `7cb28b547e7c63e2` | — | Real WF metrics; LSTM negative vs naive MAE | Partial | Keep reproducible runner |
| Ablation / regimes / explain / stats / sensitivity | IMPLEMENTED | `ml/research/*` | Diagnostic modules with tests | matching tests | — | Diagnostics ≠ causal claims | No | Keep labeling |

## Backend / persistence / API

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| FastAPI app | IMPLEMENTED | `backend/app/main.py` | Health, CORS, middleware, routers | many API tests | fastapi | Optional API key | No | Harden auth |
| PostgreSQL models + Alembic | IMPLEMENTED | `backend/app/db/`, `alembic/` | Experiments, metrics, WF, preds, backtests | db + migration tests | SQLAlchemy, Alembic, psycopg | SQLite used in unit tests | Partial | Expand provenance fields |
| Research persistence service | IMPLEMENTED | `services/research_persistence.py` | Offline bundle writer | `test_research_persistence.py` | DB | Not full experiment platform | No | Expand |
| In-process TTL cache | PARTIAL | `core/cache.py` | Market OHLCV cache ~60s | `test_cache_reliability.py` | — | Not Redis | No | Shared cache if needed |
| Backend configuration | IMPLEMENTED | `backend/app/core/config.py` | Typed env settings | config tests | — | — | Partial | Keep |
| Domain contracts | IMPLEMENTED | `ml/contracts/` | Boundary specs | `test_domain_contracts.py` | — | — | Partial | Keep |
| Model registry | PARTIAL | `ml/registry/` | Filesystem registry | `test_model_registry.py` | — | Empty default | No | Wire checkpoints |
| Monitoring / drift | PARTIAL | `ml/monitoring/` | PSI/KS + rolling errors | `test_monitoring.py` | — | Not scheduled | No | Jobs |
| News / NLP / AI | PARTIAL | `ml/news`, `ml/nlp`, `ml/ai` | Ports + keyword sentiment + tools | matching tests | — | Null news; no LLM | No | Providers |
| Background jobs | PARTIAL | `backend/app/jobs/` | In-process queue | `test_job_queue.py` | — | No Redis/Celery | No | Workers |
| Auth | PARTIAL | `core/auth.py` | Optional API key | `test_auth.py` | — | No user accounts | No | User platform |

## Frontend

| Capability | Status | Location | Important files | Current behavior | Tests | Dependencies | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|--------------|-------------|------------|-------------|
| Research dashboard pages | IMPLEMENTED | `frontend/app/` | Market, features, models, experiments, WF, backtests | vitest unit tests (shallow) | Next.js, Recharts | Depends on API/DB populated | Partial | UX polish; no fake metrics |
| API client contracts | IMPLEMENTED | `frontend/lib/api/` | Typed fetch, contract list | client/contract tests | — | Some endpoints unused | Partial | Keep parity tests |
| Decorative hero graphic | PLACEHOLDER | `components/brand/HeroGraphic.tsx` | Hardcoded SVG path | — | — | Not empirical | N/A | Keep labeled decorative |
| Auth UI | NOT IMPLEMENTED | — | — | — | — | — | No | Phase 12 |

## News / NLP / AI copilot

| Capability | Status | Notes |
|------------|--------|-------|
| News ingestion | PARTIAL | Port + null provider; live credentials not configured |
| Sentiment / NLP | PARTIAL | Keyword lexicon baseline + PIT features; not SOTA |
| AI research copilot | PARTIAL | Evidence tools + safety; LLM provider not wired |

## Ops / quality

| Capability | Status | Location | Important files | Current behavior | Tests | Limitations | Prod-ready | Next action |
|------------|--------|----------|-----------------|------------------|-------|-------------|------------|-------------|
| Pytest suite | IMPLEMENTED | `tests/` | 301 collected | 300 passed, 1 skipped locally | — | Postgres migration skip without DATABASE_URL | Partial | Keep green |
| Frontend vitest | PARTIAL | `frontend/` | 14 tests | Pass on Node 20+; fail Node 18 ESM; **engines + .nvmrc enforce ≥20** | — | Node version sensitivity mitigated | Partial | Keep CI on Node 22 |
| Ruff lint | IMPLEMENTED | CI + local | backend/tests/ml/scripts | All checks passed | — | — | Partial | Keep |
| GitHub Actions CI | IMPLEMENTED | `.github/workflows/ci.yml` | backend, frontend, database jobs | CI config present | — | Not re-run in this audit against GH | Partial | Verify on PR |
| Docker Compose | IMPLEMENTED | `docker-compose.yml`, Dockerfiles | postgres + api + frontend | Local stack; **docker reqs pinned** | — | Dev credentials only | No | Harden for deploy |
| Repo health check | IMPLEMENTED | `scripts/check_repo_health.py` | Structural invariants | Local + pytest | — | Not a substitute for CI | Partial | Keep |
| Logging / metrics / observability | PARTIAL | `core/logging.py`, middleware | Structured-ish logs, request id | some API tests | — | No metrics backend/tracing | No | Phase 8/15 |
| Security (headers, size limits) | PARTIAL | `core/security.py` | Headers + body limits; no auth | `test_api_security.py` | — | Open endpoints | No | Phase 14 |
| Model monitoring / drift | NOT IMPLEMENTED | — | Future Phase 5 | — | — | — | No | Phase 5 |

---

## Summary counts (meaningful capabilities above)

Approximate: **IMPLEMENTED ~35**, **PARTIAL ~12**, **PLACEHOLDER ~2**, **NOT IMPLEMENTED ~15**, **BROKEN 0**, **UNKNOWN 0** for audited areas.

Highest-value existing core: leakage-aware ML research engine + FastAPI/Postgres/Next.js read path.  
Largest product gaps vs final platform goal: auth, jobs, news/NLP, monitoring, portfolio, cloud ops, and executed empirical provenance.
