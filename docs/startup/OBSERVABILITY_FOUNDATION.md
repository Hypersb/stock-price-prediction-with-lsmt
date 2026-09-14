# Observability Foundation

**Status:** PARTIAL (Stage A)  
**Not yet:** OpenTelemetry exporters, metrics backends, distributed tracing

## CURRENT

| Capability | Location | Notes |
|------------|----------|-------|
| Logging config | `backend/app/core/logging.py` | level from settings |
| Request IDs | middleware | correlate API logs |
| Health | `/health` | liveness |
| Ready | `/ready` | dependency check when configured |
| Safe config summary | `safe_settings_summary` | no secrets |

## Rules

1. Never log passwords, tokens, API keys, or full connection strings with credentials.  
2. Domain code may use standard library logging; prefer structured key=value messages.  
3. Unexpected API exceptions map to generic `internal_error` responses.  
4. Full metrics/tracing remain later stages (TD-016).
