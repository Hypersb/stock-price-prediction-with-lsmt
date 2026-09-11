# Frontend Dashboard

Next.js + TypeScript quantitative research dashboard over the FastAPI backend.
The research pipeline is offline; pages primarily **read persisted artifacts**.

## Architecture

```text
browser
  → Next.js App Router pages
  → typed API client (lib/api)
  → FastAPI /api/v1
  → PostgreSQL + quantitative engine
```

Pages are mostly server components. Interactive controls and charts use client components.

## Setup

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | FastAPI origin, e.g. `http://localhost:8000` |
| `API_INTERNAL_BASE_URL` | Optional Docker SSR override (server-only) |

Only `NEXT_PUBLIC_*` values are available in the browser. Never put database passwords or private keys in frontend environment variables.

## FastAPI Connection

The dashboard calls (among others):

- `GET /api/v1/health` · `GET /api/v1/ready`
- `GET /api/v1/market-data/{symbol}` (limit/offset + pagination metadata)
- `GET /api/v1/analysis/{symbol}/summary`
- `GET /api/v1/features/{symbol}` (limit/offset)
- `GET /api/v1/models`
- `GET /api/v1/models/{model}/predictions/{symbol}` (persisted OOS only; never trains)
- `GET /api/v1/experiments` · `/{id}` · `/{id}/metrics` · `/{id}/related`
- `GET /api/v1/walk-forward/{run_id}`
- `GET /api/v1/backtests` · `/{id}`

## Page Structure

| Route | Purpose |
|-------|---------|
| `/` | Overview and backend health |
| `/market` | Market OHLCV summary/charts; shows pagination metadata (`limit` / `offset`) |
| `/features` | Feature explorer |
| `/models` | Supported model catalog |
| `/experiments` | Experiment history |
| `/experiments/[id]` | Experiment detail, metrics, and **related** walk-forward / backtest links |
| `/walk-forward` | Walk-forward fold analytics for a persisted run id |
| `/backtests` | Backtest and risk dashboard for persisted (or selectable) runs |

## Distinguishing Data Views

| View | What it is | What it is not |
|------|------------|----------------|
| Market | Historical OHLCV inspection | Model forecasts |
| Predictions | Persisted OOS model outputs from PostgreSQL | On-demand training |
| Walk-forward / OOS | Fold structure and true OOS collections | Continuous live streaming |
| Backtests | Historical strategy simulation on OOS inputs / stored runs | Live trading or brokerage |

Experiment detail loads `GET /experiments/{id}/related` and links to
`/walk-forward?run_id=…` and `/backtests?id=…` when artifacts exist.

## Charting Library

`recharts` is used for time-series lines (prices, cumulative returns, equity, drawdown).

## TypeScript API Client

Centralized under `frontend/lib/api`:

- shared `apiFetch`
- domain helpers for market, features, models, experiments, backtests
- typed contracts in `frontend/types/api.ts`

Errors become `ApiError` instances and surface as empty/error panels rather than fabricated numbers.

## Testing

```powershell
npm run lint
npm run typecheck
npm test
npm run build
```

## Limitations

- No authentication
- No live trading / brokerage screens
- Walk-forward view requires an explicit persisted run id
- Charts and tables depend on real API data; empty states appear when persistence has no rows
- Browser never connects to PostgreSQL directly
