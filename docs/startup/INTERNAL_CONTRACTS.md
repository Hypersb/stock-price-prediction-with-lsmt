# Internal Contracts

Prompt 4 living contracts for the modular research monolith.  
Code lives primarily under `ml/contracts/` and existing domain modules.

Canonical research flow (**CURRENT** unless marked FUTURE):

```text
Provider (Yahoo adapter)                    CURRENT
  → Market Data (OHLCV validate/normalize)  CURRENT
  → DatasetSpec metadata                    CONTRACT (minimal)
  → Features + Target                       CURRENT + CONTRACT specs
  → Model (Predictor / LSTM wrappers)       CURRENT + Protocol
  → Prediction (OOS tables / PredictionRecord) CURRENT + CONTRACT
  → Evaluation                              CURRENT
  → Signal                                  CURRENT
  → Backtest (h=1 only)                     CURRENT
  → Risk metrics (Sharpe/DD/…)              CURRENT (split ownership)
  → ExperimentSpec / ArtifactRef            CONTRACT (minimal)
  → Application service                     CURRENT
  → API schemas                             CURRENT
  → Frontend                                CURRENT
```

---

## Market data

- **Columns:** `date, open, high, low, close, volume` (`REQUIRED_COLUMNS`)  
- **Adjustment:** **unadjusted** (`auto_adjust=False`) — explicit; TD-001  
- **Range:** provider requests are half-open (start inclusive, end exclusive)  
- **Provider port:** `MarketDataProvider`; only `ml.data.yahoo` imports yfinance  

## Dataset

`DatasetSpec`: `dataset_id`, symbol, provider, dates, frequency, raw/derived, adjustment_policy, optional feature/target refs.  
Not a DB table yet.

## Features

- Built by `build_features` from validated OHLCV; trailing windows only  
- Warm-up → NaNs; dropped later by boundaries  
- Must not download data or train models  
- `FeatureSetSpec` names feature columns + lookback for provenance  

## Targets

- `future_return_h = close_{t+h}/close_t - 1`  
- Direction: `1` iff future return `> 0` (flats → `0`; NA preserved)  
- `TargetSpec` encodes kind/horizon/column naming  

## Models

- Tabular baselines expose `fit`/`predict` (`Predictor` Protocol)  
- LSTM remains sequence-specific; walk-forward adapters wrap it  
- No forced inheritance hierarchy  

## Predictions

- Walk-forward collector builds date/fold/model/actual/predicted tables  
- `PredictionRecord` is the typed provenance-ready row shape (optional fields stay optional)  

## Evaluation

- `ml.evaluation` owns predictive metrics (MAE/RMSE/…, clf metrics)  
- Must not train, download, or backtest  
- Metric name sets listed in `ml.contracts.evaluation`  

## Walk-forward

- Inputs: features/targets, model factory, `WalkForwardConfig` (folds, purge, gap)  
- Retrains per fold; train-only scalers  
- Outputs: fold metrics + OOS prediction table  
- No HTTP/UI imports  

## Backtest

```text
predictions → signals → align(h=1) → costs → equity → metrics
```

- Does not retrain models  
- Does not fetch alternate market history inside the engine  
- `forecast_horizon != 1` → `BacktestError` (fail-loud)  

## Risk

- **CURRENT:** drawdown/vol/Sharpe/Sortino/hit-rate via analysis + backtest metrics  
- **FUTURE:** VaR/ES/beta/factors/portfolio risk — not implemented  

## Experiment / artifacts

- `ExperimentSpec` links ids for provenance (no fake metrics)  
- `ArtifactRef` points at filesystem paths/kinds under `QUANT_ARTIFACT_ROOT`  
- Full registry/object storage is FUTURE (Phases 4–15 product roadmap)  

## Application / API

- Routes: validate → service → map DTO  
- Services orchestrate `ml` + repositories  
- `ml` must not import FastAPI/schemas/frontend  

## Domain errors

`ml.errors`: `DomainError`, `DataProviderError`, `DataValidationError`, `ModelError`, `EvaluationError`, `BacktestError`, `ArtifactError`.  
HTTP mapping remains `backend.app.core.errors` (Prompt 8 expands observability).
