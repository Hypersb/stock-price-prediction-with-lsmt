# Configuration Architecture

Audit/implementation date: 2026-09-13 (Prompt 3)

Canonical ownership: **`backend.app.core.config`** for backend/runtime infrastructure.  
Frontend public config: **`frontend/lib/env.ts`**.  
Research/experiment parameters: **`ml/*/config.py`** (not process env).

---

## Precedence

1. Process environment variables already set (Compose, CI, shell export, platform secrets)  
2. Repo-root `.env` keys **only when** `APP_ENV=development` (default) or test with `QUANT_LOAD_DOTENV=true`  
3. Safe environment-specific defaults in code  

**Production never loads `.env` files.**

---

## Environments

| Environment | Purpose | Defaults | Strictness |
|-------------|---------|----------|------------|
| `development` | Local DX | localhost CORS, optional DB, DEBUG logs, dotenv on | Lenient |
| `test` | Pytest/CI hermetic runs | localhost CORS, dotenv off, non-local DB refused | Isolated |
| `production` | Deployed API | No CORS defaults, `DATABASE_URL` required, no dotenv | Fail-fast |

Unsupported names (e.g. `staging`) raise `ConfigurationError`.

---

## Logical settings groups (single `Settings` object)

| Group | Fields |
|-------|--------|
| Application | `app_env`, `app_name`, `app_version`, `api_v1_prefix`, `log_level` |
| CORS / network | `cors_origins`, `cors_allow_credentials`, methods/headers |
| Database | `database_url`, `require_database` |
| Market data / cache | provider, limits, TTL, cache size, optional API key |
| Paths | `data_root`, `artifact_root` |

No second settings framework was introduced; typed frozen dataclass + validators.

---

## Secret classification

| Class | Examples | Rules |
|-------|----------|-------|
| PUBLIC | `NEXT_PUBLIC_API_BASE_URL`, CORS origins | Safe in browser / docs |
| INTERNAL | pool/page limits, TTL, log level, provider name, paths | Server-side; OK in safe summary |
| SECRET | `DATABASE_URL` password, `MARKET_DATA_API_KEY` | Never in logs, health, safe summary, or `NEXT_PUBLIC_*` |

Diagnostics: `Settings.safe_settings_summary()` + `python -m scripts.print_config`.

---

## Frontend boundary

| Variable | Visibility |
|----------|------------|
| `NEXT_PUBLIC_API_BASE_URL` | CLIENT-EXPOSED |
| `API_INTERNAL_BASE_URL` | SERVER-ONLY (SSR/Docker) |
| Backend secrets | Never |

---

## Database safety

- Alembic and the API both read `DATABASE_URL` from the environment.  
- `APP_ENV=production` requires `DATABASE_URL`.  
- `APP_ENV=test` refuses non-local DB hosts unless `ALLOW_NONLOCAL_TEST_DATABASE=true`.  
- Pytest autouse fixture forces `APP_ENV=test`, disables dotenv, strips ambient API keys and non-local DB URLs.

---

## Market provider configuration

- `MARKET_DATA_PROVIDER` currently allows only `yahoo`.  
- Cache TTL/size and row/day limits are explicit settings.  
- Optional `MARKET_DATA_API_KEY` reserved; empty by default.  
- Yahoo `auto_adjust` behavior remains code-level (research debt TD-001), not a silent env flip in this prompt.

---

## Experiment vs infrastructure

Infrastructure env vars must not absorb:

- lookback, horizon, feature sets  
- seeds, epochs, learning rates  
- walk-forward window sizes  
- transaction-cost assumptions  

Those remain in `ml` config objects and future provenance records.

---

## Paths

- Default data root: `<repo>/data` (`QUANT_DATA_ROOT` override)  
- Default artifact root: `<repo>/artifacts` (`QUANT_ARTIFACT_ROOT` override)  
- CSV store: `ml.data.storage.default_raw_data_directory()` respects `QUANT_DATA_ROOT`  

---

## CORS

- Development/test default to local Next origins.  
- Production requires explicit origins (or empty for non-browser).  
- Wildcard `*` is rejected.  
- Credentials + wildcard is rejected.

---

## Docker / CI

- Compose injects env; does not COPY `.env` into images.  
- `QUANT_LOAD_DOTENV=false` in Compose backend service.  
- CI: Python 3.12, Node 22, `APP_ENV=test` — matches local docs (Node ≥20).  

See also: [`CONFIGURATION_CONTRACT.md`](CONFIGURATION_CONTRACT.md).
