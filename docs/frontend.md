# Frontend Dashboard

Phase 13 provides a Next.js + TypeScript quantitative research dashboard for the FastAPI backend.

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

Only `NEXT_PUBLIC_*` values are available in the browser. Never put database passwords or private keys in frontend environment variables.

## Development Server

```powershell
npm run dev
```

## FastAPI Connection

Start the backend from the repository root:

```powershell
uvicorn backend.app.main:app --reload
```

The dashboard calls:

- `GET /api/v1/health`
- `GET /api/v1/market-data/{symbol}`
- `GET /api/v1/analysis/{symbol}/summary`
- `GET /api/v1/features/{symbol}`
- `GET /api/v1/models`
- `GET /api/v1/experiments`
- `GET /api/v1/experiments/{id}`
- `GET /api/v1/experiments/{id}/metrics`
- `GET /api/v1/walk-forward/{run_id}`
- `GET /api/v1/backtests`
- `GET /api/v1/backtests/{id}`

## Page Structure

| Route | Purpose |
|-------|---------|
| `/` | Overview and backend health |
| `/market` | Market summary and charts |
| `/features` | Feature explorer |
| `/models` | Supported model catalog |
| `/experiments` | Experiment history |
| `/experiments/[id]` | Experiment detail and metrics |
| `/walk-forward` | Walk-forward fold analytics |
| `/backtests` | Backtest and risk dashboard |

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
