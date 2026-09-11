# Research Methodology

## Research Question

Can an LSTM time-series model improve **out-of-sample predictive performance**
and **economic usefulness** relative to simpler baselines (naive,
linear/logistic, tree ensembles) for short-horizon equity return/direction
forecasting, under leakage-safe chronological evaluation?

A negative answer is scientifically valid.

## Data

- Historical OHLCV via a provider abstraction (Yahoo Finance implementation).
- Validation and normalization precede research transforms.
- Multi-asset evaluation uses a configurable universe; the default example
  (`AAPL`, `MSFT`, `JPM`, `XOM`, `SPY`) is illustrative only.
- Unit tests use deterministic synthetic fixtures and do not download market data.

## Target Definitions

- Regression: future simple return at horizon `h` (`future_return_{h}`).
- Classification: binary direction of the future return at horizon `h`
  (`direction_{h}`).
  - When a future return is defined: `1` if `future_return > 0`, else `0`
    (flat / non-positive are non-up).
  - Missing future returns remain NA and are **not** coerced to class 0.
- Targets are constructed separately from features and validated for integrity.

## Features

Leakage-aware features include:

- lagged simple/log returns
- momentum
- SMA / EMA and price-to-average ratios
- rolling volatility and ATR
- volume change / relative volume
- RSI and MACD

Feature quality validation and prefix-invariance tests guard against using
future rows to rewrite historical feature values.

## Leakage Controls

- Features use only information available at or before each timestamp.
- Targets are separated from the feature matrix.
- Chronological splits preserve temporal order.
- Scalers and fold preprocessors fit on training rows only.
- Walk-forward folds apply forecast-horizon purging and optional gaps.
- Regime labels use trailing moving averages, trailing returns, and expanding
  causal volatility quantiles (no full-sample future thresholds).
- Final holdout/test data is not used for threshold tuning or model selection.

## Models

- Naive regression / naive direction
- Linear regression / logistic regression
- Random forest
- Gradient boosting
- PyTorch LSTM regression / classification

LSTM lookback sequences for a fold partition may include earlier **within-fold**
feature rows as context only. Targets and target dates come from the evaluation
partition; context-partition targets are never used as labels.

## Chronological Splits and Walk-Forward Validation

- Expanding and rolling walk-forward configurations are supported.
- Each fold trains fresh models, evaluates only its test window, and emits
  true out-of-sample predictions.
- Aggregate stability metrics summarize fold variability without deleting bad folds.

## Regime Analysis

Rule-based trend (`bullish` / `bearish` / `neutral`) and volatility
(`low` / `normal` / `high`) labels. Thresholds are explicit and configurable.
Minimum observation counts gate interpretation. Labels are diagnostics, not
causal claims.

## Explainability

- Tree native impurity importance where available
- Linear/logistic coefficients with scaling caveats
- Permutation importance on evaluation-safe partitions
- LSTM permutation-based sequence feature sensitivity (sensitivity, not causal
  attribution)

SHAP is not required for this phase.

## Ablation

Logical feature groups (returns, momentum, trend, volatility, volume,
technical) are removed one group at a time on aligned chronological splits.
Absolute and relative metric changes are reported without automatic claims of
practical significance for tiny differences.

## Statistical Comparison

Paired out-of-sample predictions are compared with a moving block bootstrap for
selected metrics (for example MAE or directional accuracy differences). A
confidence interval covering zero does **not** prove models are identical.

## Backtesting Assumptions

- Signals from OOS predictions only
- Forward execution alignment (no lookahead)
- Strategy backtesting / execution alignment supports **`forecast_horizon=1`
  only**
- Configurable transaction costs and slippage in basis points
- Gross/net returns, equity curve, Sharpe, Sortino, drawdown, turnover, exposure
- Exact-date buy-and-hold benchmark on the matching OOS realization window

### Fold-aware OOS stitching

Walk-forward OOS series are not silently treated as one continuous daily
portfolio when folds leave gaps or overlapping realization dates:

- Overlapping prediction dates across folds **reject** a combined continuous
  backtest.
- Discontinuous calendars omit combined continuous annualization (no inventing
  continuity across gaps).
- Per-fold backtests remain valid regardless of stitching.

## Transaction Costs and Sensitivity

Default diagnostic cost scenarios include 0, 5, 10, and 25 bps. Threshold
sweeps are diagnostic; selecting thresholds on the final test period is
forbidden for unbiased claims.

## Limitations

- Not live trading advice; no brokerage execution.
- Data quality and corporate-action handling depend on the provider.
- Model timings are local diagnostics.
- Economic metrics inherit strategy-rule and cost assumptions.
- The project must not claim profitability without evidence.

## Implementation Entry Points

- `ml/research/pipeline.py` — final orchestration
- `ml/research/config.py` — reproducible configuration + fingerprint
- `ml/research/report.py` — report rendering without fabricated numbers
- `docs/final-research-report.md` — report template / populated output location
