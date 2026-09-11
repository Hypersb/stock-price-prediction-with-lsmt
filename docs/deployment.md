# Deployment and Production Readiness

This document describes how to run the modular monolith reliably. “Production ready” here means reproducible builds, clear configuration, migrations, health/readiness checks, CI, tested interfaces, secure defaults, and documented startup. It does **not** mean infinite scale, audited financial software, profitable predictions, or institutional trading infrastructure.

## Architecture

```text
Browser
  → Next.js dashboard
  → FastAPI /api/v1
       ├── PostgreSQL (research persistence)
       └── Quantitative / ML engine (in-process)
```

Keep the system a modular monolith. Do not introduce microservices for this project.

## Environment Variables

Copy `.env.example` to a local `.env` (never commit secrets).

| Variable | Layer | Notes |
|----------|-------|-------|
| `APP_ENV` | backend | `development`, `production`, or `test` |
| `DATABASE_URL` | backend | Required when `APP_ENV=production` |
| `FRONTEND_ORIGIN` / `CORS_ORIGINS` | backend | Trusted browser origins; empty by default in production |
| `MAX_MARKET_DATA_DAYS` | backend | Caps historical range size |
| `MAX_MARKET_ROWS` | backend | Caps OHLCV rows returned per market-data request |
| `MAX_FEATURE_ROWS` | backend | Caps feature JSON payload rows |
| `MAX_PAGE_SIZE` | backend | Caps list pagination |
| `MAX_REQUEST_BODY_BYTES` | backend | Rejects oversized POST bodies (streaming enforcement) |
| `MARKET_DATA_CACHE_TTL_SECONDS` | backend | In-process market-data cache TTL |
| `MARKET_DATA_API_KEY` | backend | Optional provider credential; never expose publicly |
| `NEXT_PUBLIC_API_BASE_URL` | frontend | Browser-visible API origin only |
| `API_INTERNAL_BASE_URL` | frontend server | Optional Docker SSR override (not `NEXT_PUBLIC_`) |

Never place database passwords or private keys in `NEXT_PUBLIC_*` variables.

## Backend Startup

```powershell
# from repository root, with venv active
$env:DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/quant_research"
alembic upgrade head
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Build

The Compose/production frontend image is **multi-stage**: install deps →
`npm run build` → `npm run start` on the runner stage (not `next dev`).

```powershell
cd frontend
npm ci
copy .env.example .env.local
npm run build
npm run start
```

Development:

```powershell
npm run dev
```

## PostgreSQL

Local Docker database only:

```powershell
docker compose up postgres -d
```

Apply schema with Alembic. Do not use `create_all()` as a production migration substitute.

## Docker Compose

Full stack (Postgres + FastAPI + Next.js):

```powershell
docker compose config
docker compose build
docker compose up
```

Development Compose credentials (`user` / `password`) are placeholders only.

- Backend entrypoint runs `alembic upgrade head`, then Uvicorn.
- Frontend browser calls `http://localhost:8000`.
- Frontend SSR uses `API_INTERNAL_BASE_URL=http://backend:8000`.

## Health and Readiness

- `GET /api/v1/health` — process liveness (no dependency probes).
- `GET /api/v1/ready` — dependency readiness (database connectivity). Returns `503` when not ready. Never exposes `DATABASE_URL` or credentials.

## Continuous Integration

GitHub Actions workflow: `.github/workflows/ci.yml`

Jobs:

1. Backend — Ruff + pytest (CPU Torch)
2. Frontend — lint, typecheck, tests, production build
3. Database — Postgres service, Alembic upgrade, persistence tests

CI does not require local `.env`, Yahoo Finance, GPUs, or production secrets.

## Security Assumptions

**Security boundary = local / private research**, not a public multi-user
trading product.

- No authentication (intentional for single-operator research).
- CORS allowlists trusted origins.
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`.
- Streaming request body size limits and market/feature/pagination caps (`MAX_MARKET_ROWS` included).
- Ticker path validation.
- Unexpected errors return generic envelopes (no stack traces to clients).
- No brokerage connectivity or live order execution.

## Artifact Handling

Do not deploy or commit:

- `.env` / `.env.local`
- datasets under `data/raw` or `data/processed`
- model checkpoints (`*.pt`, `checkpoints/`)
- `.venv`, `node_modules`, `.next`
- Docker volume contents

Checkpoint references may be stored as paths/URIs; weights are not stored in PostgreSQL.

## Limitations

- Yahoo Finance access is optional for local demos; tests use deterministic fixtures.
- Walk-forward and experiment history require persisted rows.
- In-process market-data cache is single-process only (no Redis).
- Not a brokerage or real-money trading system.
