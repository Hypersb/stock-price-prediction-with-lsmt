# Backend API

Phase 11 exposes the quantitative research engine through a FastAPI HTTP boundary.

## Architecture

```text
HTTP client / future Next.js frontend
        |
        v
FastAPI routes (/api/v1)
        |
        v
Pydantic request/response schemas
        |
        v
application services
        |
        v
existing ml/ domain modules
```

Routes stay thin. Quantitative formulas remain in `ml/`. Services adapt validated API inputs to existing ingestion, analysis, feature, model-metadata, and backtesting functionality.

## Local Startup

From the repository root, with the project virtual environment activated:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload
```

Health check:

```text
GET http://127.0.0.1:8000/api/v1/health
```

Interactive OpenAPI docs:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/openapi.json
```

## Configuration

Environment variables (see `.env.example`):

- `APP_ENV` — `development` or `production`
- `APP_NAME` / `APP_VERSION` — service metadata returned by health
- `FRONTEND_ORIGIN` — single allowed browser origin
- `CORS_ORIGINS` — comma-separated allowed origins (overrides frontend origin when set)
- `MAX_MARKET_DATA_DAYS` — maximum request span for market-data queries
- `MAX_FEATURE_ROWS` — maximum feature rows returned by the features API

Production-oriented configuration does not default to allowing every origin. If `APP_ENV=production` and no origin configuration is provided, CORS origins are empty.

## API Versioning

All research endpoints are versioned under:

```text
/api/v1
```

## Major Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Service health |
| GET | `/api/v1/market-data/{symbol}` | Historical OHLCV |
| GET | `/api/v1/analysis/{symbol}/summary` | Return/risk summary |
| GET | `/api/v1/features/{symbol}` | Engineered feature inspection |
| GET | `/api/v1/models` | Supported model catalog |
| GET | `/api/v1/models/{model}/predictions/{symbol}` | Stored predictions only |
| POST | `/api/v1/backtests` | Out-of-sample research backtest |

## Request/Response Concepts

- Market-data and analysis queries accept `start_date` and optional `end_date`.
- Feature responses include feature names and bounded observation rows. Target columns are never exposed.
- Model catalog entries report supported families. `trained=false` unless a future persistence layer supplies artifacts.
- Prediction GET endpoints never train models. Missing artifacts return `available=false`.
- Backtests require `sample_kind=out_of_sample` plus explicit prediction and realized-return payloads.

## Error Handling

Errors use a stable envelope:

```json
{
  "error": "bad_request",
  "detail": "human-readable message",
  "code": "bad_request"
}
```

- Validation failures: `422`
- Domain/client errors: `400`
- Missing resources: `404`
- Unexpected failures: `500` without stack traces or secrets

## CORS

CORS is configured from environment settings. Development defaults allow local Next.js origins (`http://localhost:3000` and `http://127.0.0.1:3000`). Production requires explicit origin configuration.

## Observability

- Startup/shutdown logging via FastAPI lifespan
- Per-request access logs with method, path, status, and duration
- `X-Request-ID` request/response header correlation
- Sensitive headers are not logged

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check backend tests
```

API tests use FastAPI `TestClient` and inject fake market-data providers. Normal tests do not require internet access and do not train LSTMs.

## Current Limitations

- No PostgreSQL or experiment persistence yet
- No authentication or user accounts
- No background training jobs
- No live market streaming, brokerage, or trading execution
- Predictions are only returned when an in-process store has been populated (placeholder for Phase 12)
- Backtests accept explicit OOS payloads rather than loading stored experiment IDs
