# Backend API

FastAPI exposes the quantitative research platform through a versioned HTTP
boundary. Routes stay thin; persistence and domain work live behind services.

## Architecture

Two primary call paths:

```text
HTTP client / Next.js
        │
        ▼
FastAPI routes (/api/v1)
        │
        ▼
application services
        │
        ├── repositories ──► PostgreSQL
        │
        └── ml/ domain modules (ingestion, analysis, features, backtesting, …)
```

- **Routes** validate path/query/body inputs and return Pydantic schemas.
- **Services** adapt API inputs to repositories and/or `ml/` engines.
- **Repositories** own SQLAlchemy access to experiments, walk-forward runs,
  out-of-sample predictions, metrics, and backtests.
- Quantitative formulas remain in `ml/`; the API does not reimplement them.

## Local Startup

From the repository root, with the project virtual environment activated and
`DATABASE_URL` set when persistence is required:

```bash
alembic upgrade head
uvicorn backend.app.main:app --reload
```

Health and readiness:

```text
GET http://127.0.0.1:8000/api/v1/health
GET http://127.0.0.1:8000/api/v1/ready
```

Interactive OpenAPI docs:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/openapi.json
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Purpose |
|----------|---------|
| `APP_ENV` | `development`, `production`, or `test` |
| `APP_NAME` / `APP_VERSION` | Service metadata returned by health |
| `DATABASE_URL` | PostgreSQL URL (required in production) |
| `FRONTEND_ORIGIN` | Single allowed browser origin |
| `CORS_ORIGINS` | Comma-separated origins (overrides frontend origin when set) |
| `MAX_MARKET_DATA_DAYS` | Maximum request span for market-data queries |
| `MAX_MARKET_ROWS` | Cap on OHLCV rows returned per request |
| `MAX_FEATURE_ROWS` | Cap on feature rows returned by the features API |
| `MAX_PAGE_SIZE` / `DEFAULT_PAGE_SIZE` | List/pagination caps |
| `MAX_REQUEST_BODY_BYTES` | Streaming body-size enforcement |
| `MARKET_DATA_CACHE_TTL_SECONDS` | In-process market-data cache TTL |

Production-oriented configuration does not default to allowing every origin. If
`APP_ENV=production` and no origin configuration is provided, CORS origins are
empty.

## API Versioning

All research endpoints are versioned under `/api/v1`.

## Major Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Process liveness (no dependency probes) |
| GET | `/api/v1/ready` | Dependency readiness (database connectivity); `503` when not ready |
| GET | `/api/v1/market-data/{symbol}` | Historical OHLCV with `limit` / `offset` pagination metadata |
| GET | `/api/v1/analysis/{symbol}/summary` | Return / risk summary |
| GET | `/api/v1/features/{symbol}` | Engineered feature inspection with `limit` / `offset` |
| GET | `/api/v1/models` | Supported model catalog |
| GET | `/api/v1/models/{model}/predictions/{symbol}` | Persisted OOS predictions from PostgreSQL |
| GET | `/api/v1/experiments` | Experiment list (paginated) |
| GET | `/api/v1/experiments/{id}` | Experiment detail |
| GET | `/api/v1/experiments/{id}/metrics` | Stored experiment metrics |
| GET | `/api/v1/experiments/{id}/related` | Linked walk-forward runs and backtests |
| GET | `/api/v1/walk-forward/{run_id}` | Walk-forward run + fold analytics |
| POST | `/api/v1/backtests` | Synchronous research backtest from explicit OOS payloads |
| GET | `/api/v1/backtests` | Persisted backtest list (paginated) |
| GET | `/api/v1/backtests/{id}` | Persisted backtest detail, metrics, equity curve |

## Predictions

`GET /api/v1/models/{model}/predictions/{symbol}` **never trains models**.

It reads `OutOfSamplePrediction` rows through `PredictionRepository` (optional
filters: `experiment_id`, `walk_forward_run_id`, date range, `limit` /
`offset`). When no matching rows exist, the response reports
`available=false` rather than inventing forecasts.

## Request/Response Concepts

- Market-data and analysis queries accept `start_date` and optional `end_date`.
- Market-data responses include `total`, `count`, `limit`, `offset`, and
  `returned` so clients can page without guessing completeness.
- Feature responses include feature names and bounded observation rows. Target
  columns are never exposed.
- Model catalog entries report supported families. `trained=false` unless
  persistence indicates otherwise for a future artifact layer.
- Backtests require `sample_kind=out_of_sample`. `POST /backtests` accepts
  explicit prediction and realized-return payloads; `GET /backtests` reads
  persisted runs.

## Security

Authentication is intentionally omitted for local / private research use. The
HTTP boundary still enforces:

- **Request body size**: streaming enforcement via
  `RequestSizeLimitMiddleware` (Content-Length early reject plus byte counting
  so chunked bodies cannot bypass `MAX_REQUEST_BODY_BYTES`)
- **CORS**: allowlisted origins from environment settings
- **Ticker validation**: path symbols must match a bounded alphanumeric pattern
- **Security headers**: `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy`
- Caps on market rows, feature rows, date spans, and list page sizes

This is not a public multi-user trading product boundary.

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
- Payload too large: `413`
- Missing resources: `404`
- Unexpected failures: `500` without stack traces or secrets

## CORS

CORS is configured from environment settings. Development defaults allow local
Next.js origins (`http://localhost:3000` and `http://127.0.0.1:3000`).
Production requires explicit origin configuration.

## Observability

- Startup/shutdown logging via FastAPI lifespan
- Per-request access logs with method, path, status, and duration
- `X-Request-ID` request/response header correlation
- Sensitive headers are not logged

## Testing

```bash
ruff check backend tests
pytest -q
```

API tests use FastAPI `TestClient` and inject fake market-data providers. Normal
tests do not require internet access and do not train LSTMs.

## Current Limitations

These remain true:

- No authentication or user accounts (intentional for local/private research)
- No background training or job queue
- No live market streaming, brokerage connectivity, or trading execution
- Strategy backtesting / execution alignment requires `forecast_horizon=1`
- `POST /api/v1/backtests` runs synchronously from explicit OOS payloads; clients
  may alternatively `GET` previously persisted backtests
