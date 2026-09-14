# Data Contracts & Schemas

**Status:** CURRENT foundation (Stage A / Phase 1 Prompt 5 condensed)  
**Related:** `ml/contracts/`, `ml/data/schema.py`, `INTERNAL_CONTRACTS.md`

## Purpose

Make research data shapes explicit so providers, features, models, APIs, and persistence do not silently drift.

## Canonical layers

| Layer | Representation | Owner |
|-------|----------------|-------|
| Provider OHLCV | pandas columns in `REQUIRED_COLUMNS` (+ optional `adj_close`) | `ml.data` |
| Market semantics | `MarketDataSemantics` / price-basis policy | `ml.contracts.market_data` |
| Dataset identity | `DatasetSpec` + content fingerprint helpers | `ml.contracts.dataset`, `ml.data.fingerprint` |
| Feature set | `FeatureSetSpec` | `ml.contracts.features` |
| Target | `TargetSpec` | `ml.contracts.targets` |
| Prediction | `PredictionRecord` | `ml.contracts.predictions` |
| HTTP | Pydantic schemas under `backend.app.schemas` | API boundary only |

## Rules

1. Domain algorithms consume domain frames/contracts — not FastAPI models.  
2. Optional fields stay optional until legitimately populated.  
3. Changing price basis (`unadjusted` → `adjusted`) is a methodological change, not a silent rename.  
4. HTTP schemas may mirror domain fields but must not become the source of truth for ML math.

## Schema versioning

- Market OHLCV required schema version: **v1** (`date, open, high, low, close, volume`)  
- Optional extension: `adj_close` when the provider supplies it  
- Feature/target version ids live on specs; bump when formulas or column sets change intentionally
