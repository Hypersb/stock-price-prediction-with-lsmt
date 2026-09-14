# Service & API Foundation

**Status:** CURRENT foundation  
**API prefix:** `/api/v1`

## Layering

```
HTTP route (validation, status codes)
  → application service (orchestration)
    → ml domain / contracts (algorithms)
    → repositories (persistence)
```

## Route responsibilities (allowed)

- Parse/validate request models  
- Call one service method  
- Map domain/app errors to HTTP envelopes  
- Return Pydantic response models  

## Route responsibilities (forbidden)

- Feature formulas, Sharpe math, LSTM training loops  
- Direct `yfinance` imports  
- Ad-hoc SQL outside repositories  

## Error model

| Layer | Types |
|-------|-------|
| Domain | `ml.errors.DomainError` hierarchy |
| Application/API | `backend.app.core.errors.AppError` hierarchy |
| Mapping | handlers in `register_exception_handlers` — no stack traces to clients |

## Compatibility

Preserve `/api/v1` paths and response fields unless a migration note documents a breaking change. Prefer additive fields.
