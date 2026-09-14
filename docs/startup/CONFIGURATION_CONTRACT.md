# Configuration Contract

Canonical human-readable variable contract for Phase 1 Prompt 3.  
**Never store real secrets in this document.**

Legend: **Req** = required environments (`D` development, `T` test, `P` production).

| VARIABLE | OWNER | TYPE | DEFAULT | REQUIRED IN | SECRET? | CLIENT SAFE? | DESCRIPTION |
|----------|-------|------|---------|-------------|---------|--------------|-------------|
| `APP_ENV` | backend | enum | `development` | D/T/P | no | no | `development` \| `test` \| `production` |
| `APP_NAME` | backend | str | research API name | — | no | no | Service name in health payloads |
| `APP_VERSION` | backend | str | `0.1.0` | — | no | no | API version string |
| `API_V1_PREFIX` | backend | str | `/api/v1` | — | no | no | Must start with `/` |
| `LOG_LEVEL` | backend | enum | `DEBUG` (dev) / `INFO` | — | no | no | Python logging level |
| `QUANT_LOAD_DOTENV` | backend | bool | `true` (dev) / `false` (test) | — | no | no | Load repo `.env` into unset keys |
| `FRONTEND_ORIGIN` | backend | URL | — | P* | no | yes | Single CORS origin helper |
| `CORS_ORIGINS` | backend | CSV URLs | local Next (D/T) / empty (P) | P* | no | yes | Overrides `FRONTEND_ORIGIN` when set; no `*` |
| `CORS_ALLOW_CREDENTIALS` | backend | bool | `true` | — | no | no | CORS credentials flag |
| `DATABASE_URL` | backend/alembic | URL | empty | **P** | **yes** | **no** | SQLAlchemy URL; credentials are secret |
| `ALLOW_NONLOCAL_TEST_DATABASE` | backend | bool | `false` | — | no | no | Opt-in for remote DB under `APP_ENV=test` |
| `MARKET_DATA_PROVIDER` | backend | str | `yahoo` | — | no | no | Only `yahoo` supported now |
| `MARKET_DATA_API_KEY` | backend | str | empty | — | **yes** | **no** | Optional provider credential |
| `MAX_MARKET_DATA_DAYS` | backend | int>0 | `3650` | — | no | no | Request window guard |
| `MAX_MARKET_ROWS` | backend | int>0 | `5000` | — | no | no | Response row guard |
| `MAX_FEATURE_ROWS` | backend | int>0 | `500` | — | no | no | Feature page guard |
| `MAX_PAGE_SIZE` | backend | int>0 | `100` | — | no | no | Max page size |
| `DEFAULT_PAGE_SIZE` | backend | int>0 | `20` | — | no | no | Must be ≤ max page size |
| `MAX_REQUEST_BODY_BYTES` | backend | int>0 | `1048576` | — | no | no | Body size limit |
| `MARKET_DATA_CACHE_TTL_SECONDS` | backend | float>0 | `60` | — | no | no | In-process OHLCV TTL |
| `MARKET_DATA_CACHE_MAX_SIZE` | backend | int>0 | `64` | — | no | no | In-process cache entries |
| `QUANT_DATA_ROOT` | backend/ml paths | path | `<repo>/data` | — | no | no | Research data root |
| `QUANT_ARTIFACT_ROOT` | backend | path | `<repo>/artifacts` | — | no | no | Artifact root |
| `UVICORN_HOST` | docker entry | str | `0.0.0.0` | — | no | no | Container bind host |
| `UVICORN_PORT` | docker entry | str | `8000` | — | no | no | Container bind port |
| `NEXT_PUBLIC_API_BASE_URL` | frontend | URL | `http://localhost:8000` | — | no | **yes** | Browser API origin |
| `API_INTERNAL_BASE_URL` | frontend server | URL | unset | — | no | **no** | SSR/Docker internal API origin |

\*Production should set explicit browser origins when browser clients are used; empty CORS is allowed for non-browser clients.

---

## Templates

- Root: `.env.example`  
- Frontend: `frontend/.env.example`  

## Diagnostics

```bash
PYTHONPATH=. python -m scripts.print_config
```

Must never print passwords, API keys, or full credential URLs.
