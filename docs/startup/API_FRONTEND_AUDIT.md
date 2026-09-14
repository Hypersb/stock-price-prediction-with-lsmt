# API / Frontend Contract Audit

Audit date: 2026-09-13  
Scope: `backend/app/api/v1/`, `backend/app/services/`, `backend/app/contracts/`, `backend/app/schemas/`, `backend/app/db/`, `frontend/app/`, `frontend/lib/api/`, `frontend/components/`, `frontend/types/`.

---

## 1. Current APIs and what each does

Contract catalog (dashboard-consumed):  
`/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/contracts/frontend_api.py`  
Mirror list: `/Users/user/Desktop/stock-price-prediction-with-lsmt/frontend/lib/api/contracts.ts`

| Method | Path | Router | Service / layer | Kind | Notes |
|--------|------|--------|-----------------|------|-------|
| GET | `/api/v1/health` | `backend/app/api/v1/health.py` | Settings only | Process liveness | No DB, no ML |
| GET | `/api/v1/ready` | `backend/app/api/v1/health.py` | DB `SELECT 1` | Dependency readiness | 503 if DB missing/down |
| GET | `/api/v1/market-data/{symbol}` | `backend/app/api/v1/market_data.py` | `MarketDataService` → Yahoo via `ml.data` | **Live Yahoo fetch** + in-process TTL cache | Paginated OHLCV |
| GET | `/api/v1/analysis/{symbol}/summary` | `backend/app/api/v1/analysis.py` | `AnalysisService` → market data + `ml.analysis.*` | **On-demand computation** on Yahoo series | mean/median/vol/cum return/max DD |
| GET | `/api/v1/features/{symbol}` | `backend/app/api/v1/features.py` | `FeatureService` → market data + `ml.features.pipeline` | **On-demand feature engineering** | Leakage checks; no targets |
| GET | `/api/v1/models` | `backend/app/api/v1/models.py` | `ModelService.list_models` | **Hardcoded catalog** | All `trained=False` |
| GET | `/api/v1/models/{model}/predictions/{symbol}` | `backend/app/api/v1/models.py` | `ModelService.get_predictions` | **DB read** of persisted OOS preds | Never trains; **not in frontend contract / unused by UI** |
| GET | `/api/v1/experiments` | `backend/app/api/v1/experiments.py` | `ExperimentRepository` | **DB read** | Paginated list |
| GET | `/api/v1/experiments/{id}` | same | same | **DB read** | Detail |
| GET | `/api/v1/experiments/{id}/metrics` | same | same | **DB read** | Split metrics |
| GET | `/api/v1/experiments/{id}/related` | same | WalkForward + Backtest repos | **DB read** | Empty collections OK |
| GET | `/api/v1/walk-forward/{run_id}` | `backend/app/api/v1/walk_forward.py` | `WalkForwardRepository` | **DB read** | Run + folds |
| GET | `/api/v1/backtests` | `backend/app/api/v1/backtests.py` | `BacktestRepository` | **DB read** | List |
| GET | `/api/v1/backtests/{id}` | same | same | **DB read** | Metrics + equity curve |
| POST | `/api/v1/backtests` | same | `BacktestService` → `ml.backtesting` | **On-demand ML/quant engine** | Explicit OOS payload; **unused by frontend** |

### Service classification

| File | Role |
|------|------|
| `backend/app/services/market_data.py` | Yahoo ingestion adapter + TTL cache |
| `backend/app/services/analysis.py` | Live stats over OHLCV |
| `backend/app/services/features.py` | Live feature build/validate |
| `backend/app/services/models.py` | Static catalog + optional prediction DB lookup |
| `backend/app/services/backtests.py` | Synchronous OOS backtest engine |
| `backend/app/services/research_persistence.py` | Offline/CLI bundle writer (not an HTTP router) |

### Persistence / DB

ORM under `backend/app/db/models/`: experiments, metrics, walk_forward, predictions, backtest.  
Session wiring: `backend/app/db/session.py`. Experiments/backtests/walk-forward GET routes require a configured `DATABASE_URL` via `get_db_session`. Market/analysis/features/models-catalog do not require DB.

**No HTTP route trains models or runs walk-forward.** Training/persistence is offline; APIs mostly read or compute diagnostics.

---

## 2. How the frontend gets data

| Mechanism | Used? | Evidence |
|-----------|-------|----------|
| FastAPI via `apiFetch` | **Yes** — primary | `frontend/lib/api/client.ts` (`cache: "no-store"`) |
| Server Actions (`"use server"`) | **No** | No matches under `frontend/` |
| Static / mock datasets | **No** | No mock market/experiment fixtures in app code |
| Hardcoded UI defaults | **Yes** (controls only) | `appConfig.defaultSymbol = "AAPL"` in `frontend/lib/env.ts`; rolling 1y date range in `frontend/lib/format.ts` `defaultDateRange()` |
| Client navigation forms | **Yes** | `ResearchControls`, `WalkForwardRunForm` — mutate URL only, then RSC refetches |

### Page → API map

| Page | File | API helpers | Data mode |
|------|------|-------------|-----------|
| Overview | `frontend/app/page.tsx` | `getHealth`, `listExperiments`, `listBacktests`, `listModels` | Live API counts |
| Market | `frontend/app/market/page.tsx` | `getMarketData`, `getAnalysisSummary` | Live Yahoo + live analysis |
| Features | `frontend/app/features/page.tsx` | `getFeatures` | Live engineered features |
| Models | `frontend/app/models/page.tsx` | `listModels` | Hardcoded backend catalog |
| Experiments list | `frontend/app/experiments/page.tsx` | `listExperiments` | DB |
| Experiment detail | `frontend/app/experiments/[id]/page.tsx` | `getExperiment`, `getExperimentMetrics`, `getExperimentRelated` | DB |
| Walk-forward | `frontend/app/walk-forward/page.tsx` | `getWalkForwardRun` | DB (by `run_id` query) |
| Backtests | `frontend/app/backtests/page.tsx` | `listBacktests`, `getBacktest` | DB |

Types: `frontend/types/api.ts` (aligned with FastAPI schemas).  
`frontend/types/index.ts` is empty placeholder.

### Backend endpoints not wired in UI

- `GET /ready` — client exists (`getReady` in `frontend/lib/api/market.ts`) but unused in pages
- `GET /models/{model}/predictions/{symbol}` — no frontend wrapper
- `POST /backtests` — no frontend wrapper

---

## 3. Quant / ML logic duplicated in the frontend

Frontend does **not** reimplement training, feature pipelines, Sharpe, or Yahoo ingestion. Duplications are chart/aggregation helpers only:

| Location | Logic | Backend counterpart | Risk |
|----------|-------|---------------------|------|
| `frontend/app/market/page.tsx` `buildCumulativeSeries` | Compound simple returns from **paginated** `market.data` closes | `ml.analysis.cumulative` used by analysis summary on **full** series | Chart path can diverge from `analysis.cumulative_return` when `returned < total` |
| `frontend/app/backtests/page.tsx` `buildDrawdownSeries` | Peak-to-trough % from equity points | `ml.analysis.drawdown` / backtest engine metrics | Display series only; card uses persisted `maximum_drawdown` |
| `frontend/app/walk-forward/page.tsx` `summarizeMetric` | Mean/std/min/max across fold metric maps | None in API (folds stored raw) | Population std (÷n), not sample std; presentation only |
| `frontend/lib/featureNotes.ts` | Human descriptions of feature names | Feature engineering lives in `ml.features` | Copy can drift from actual column definitions |
| `frontend/components/features/FeatureExplorerClient.tsx` | Name→group heuristics | N/A | UI grouping only |

Formatting only (not quant engines): `frontend/lib/format.ts`.

---

## 4. UI showing simulated / placeholder / hardcoded / unverifiable info

### Decorative / non-empirical (OK if labeled)

| Component | Path | What it shows | Provenance |
|-----------|------|---------------|------------|
| `HeroGraphic` | `frontend/components/brand/HeroGraphic.tsx` | Stylized “OOS PATH” SVG equity shape | **Hardcoded decorative geometry** — not market data |
| Overview footer disclaimer | `frontend/app/page.tsx` | “Historical simulation only…” | Static legal copy |
| Feature notes | `frontend/lib/featureNotes.ts` + Feature explorer | Educational blurbs | **Hardcoded** text keyed by feature name patterns |
| Model `trained` column | Models page + `SUPPORTED_MODELS` | Always `no` / `trained=False` | **Hardcoded catalog**, not artifact scan |
| Default ticker / dates | `env.ts`, `format.ts`, `ResearchControls` | AAPL + last 1 year | Defaults for queries, then replaced by API |

### Empirical numbers — provenance

| UI surface | Numbers | Provenance |
|------------|---------|------------|
| Overview API / Models / Experiments / Backtests strip | health version, counts | API: health settings; models catalog length; DB totals |
| Market MetricCards (cum return, vol, max DD, mean/median) | Analysis fields | **Computed live** from Yahoo OHLCV via analysis API |
| Market latest close / chart closes / volume | OHLCV | **Live Yahoo** (TTL-cached server-side) |
| Market cumulative **chart** series | Path from closes | **Frontend recomputed** from returned page rows |
| Features metrics + chart | Feature values | **On-demand** `build_features` over Yahoo series |
| Models table | names/families/tasks | **Hardcoded** in `backend/app/services/models.py` |
| Experiments list/detail metrics | losses, status, horizons | **DB** (persisted research) |
| Walk-forward folds + stability table | fold ranges, fold metrics, aggregates | **DB** folds; aggregates **frontend** |
| Backtest metrics / equity / drawdown chart | Sharpe, returns, equity | **DB** persisted backtest; drawdown series **frontend** from equity |

### Not fabricated for empty research history

Empty experiments/backtests/walk-forward explicitly refuse fake P&L (see §5). No demo equity curves or mock Sharpes in app pages.

---

## 5. Empty DB / no-experiments handling

| State | Where | Behavior |
|-------|-------|----------|
| API unreachable | Overview, Market, Features, Models, Experiments, Backtests, Walk-forward | `StatePanel` with error detail from `ApiError` |
| No experiments | `frontend/app/experiments/page.tsx` | “No experiments yet” — prefers empty over fabricated results |
| Experiment id missing | `frontend/app/experiments/[id]/page.tsx` | “Experiment not found” + link back |
| No linked WF / backtests on experiment | same | Soft text: “No walk-forward runs…” / “No backtests…” |
| No metrics for a split | same | “No metrics stored for this split.” |
| No backtests | `frontend/app/backtests/page.tsx` | “No backtests yet” — no fabricated profitability |
| No `run_id` | `frontend/app/walk-forward/page.tsx` | “No walk-forward run selected” — no fabricated folds |
| Bad / missing run | same | “Walk-forward run unavailable” |
| No market rows | Market page | “No market data” for symbol/range |
| No features | Features page | “No features returned” |
| Empty chart series | `TimeSeriesChart` | Empty-state message inside chart |
| Related API empty collections | Backend `get_experiment_related` docstring | Returns `[]` without inventing artifacts |

`StatePanel`: `frontend/components/ui/StatePanel.tsx`.

---

## 6. Authentication status

**None.**

- No JWT, session, OAuth, API-key dependency, or login UI in frontend.
- Backend `Depends(...)` usage is settings, DB session, and service factories only.
- `backend/app/core/security.py` provides ticker validation, security headers, and request body size limits — **not** authentication.
- CORS + headers configured in `backend/app/main.py`.
- Sensitive header names are redacted in logging middleware (`Authorization`, `Cookie`, `X-API-Key`) but those auth mechanisms are not implemented.

Implication: all `/api/v1/*` endpoints are open to any client that can reach the API (subject to network/CORS).

---

## 7. Caching behavior

| Layer | Behavior | Path / config |
|-------|----------|---------------|
| Frontend `fetch` | **`cache: "no-store"`** on every `apiFetch` | `frontend/lib/api/client.ts` |
| Next.js `revalidate` / `unstable_cache` / `force-dynamic` | **Not used** | No matches in `frontend/` |
| Backend market data | In-process **TTL LRU** cache (default **60s**, max **64** keys) keyed by `(symbol, start, end)` | `backend/app/services/market_data.py`, `backend/app/core/cache.py`, settings in `backend/app/core/config.py` |
| Analysis / features | Reuse `MarketDataService.get_ohlcv` → **inherit market TTL cache** | Then recompute stats/features each request |
| Experiments / backtests / walk-forward | **No response cache** | Direct DB reads |
| Settings | `@lru_cache` on `get_settings` | `backend/app/core/config.py` |

---

## Contract drift / gaps checklist

1. Frontend contract omits `POST /backtests` and `GET /models/.../predictions/...` (intentional for read-only dashboard).
2. `getReady` is contract-listed and client-exported but unused in UI.
3. Market cumulative **chart** vs analysis cumulative **metric** can disagree under pagination.
4. Model catalog `trained` is always false — does not reflect checkpoints in DB/`checkpoint_reference`.
5. Walk-forward UI requires manual UUID entry; no list endpoint for walk-forward runs (only by id / via experiment related).
6. No auth before exposing live Yahoo pulls and persisted research metrics.

---

## File index (absolute)

### Backend API
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/api/v1/router.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/api/v1/health.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/api/v1/market_data.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/api/v1/analysis.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/api/v1/features.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/api/v1/models.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/api/v1/experiments.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/api/v1/backtests.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/api/v1/walk_forward.py`

### Backend services / contracts / schemas / db
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/services/*.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/contracts/frontend_api.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/schemas/*.py`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/backend/app/db/`

### Frontend
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/frontend/app/**/page.tsx`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/frontend/lib/api/{client,contracts,market,features,models,experiments,backtests,index}.ts`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/frontend/types/api.ts`
- `/Users/user/Desktop/stock-price-prediction-with-lsmt/frontend/components/{brand,charts,features,layout,research,ui,walkforward}/`
