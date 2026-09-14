# Research Methodology

Canonical methodology for the modular research engine. Empirical claims must
cite an `experiment_id` and artifact paths under `docs/research/empirics/` or
`artifacts/empirics/`.

## Data and price basis

- Provider abstraction with Yahoo adapter (`auto_adjust=False`).
- Default research price basis: **unadjusted** `close` (see `PRICE_BASIS_POLICY.md`).
- Optional `adj_close` may be stored; switching research basis requires a new
  dataset fingerprint and explicit documentation.
- Quality checks: required columns, chronology, duplicates, positive prices,
  OHLC consistency, gap diagnostics.

## Features and targets

- Features are trailing-only; target-like column names are forbidden.
- Regression target: future simple return at horizon `h`.
- Direction target: `1` iff defined future return `> 0`.
- Warm-up rows dropped during supervised assembly.

## Temporal validation

- Walk-forward expanding/rolling folds with `purge_fold` using `forecast_horizon`.
- Single chronological splits accept optional `forecast_horizon` purge
  (diagnostics/supervised paths pass horizon).
- Train-only scaling inside each fold.

## Models compared (startup empirics)

naive, linear, gradient boosting, LSTM — see experiment `7cb28b547e7c63e2`.

## Metrics

- Forecast: MAE, RMSE, MSE, R², directional accuracy.
- Backtest (h=1 only): returns, Sharpe, Sortino, drawdown, costs/slippage.
- Risk helpers: Calmar, historical VaR/ES, beta, tracking error.

## Limitations

- Unadjusted prices (TD-001).
- Static universe / survivorship (TD-002).
- Backtest horizon locked to 1.
- Keyword sentiment is a baseline, not a financial transformer.
- No guarantee of future performance; negative ML results are valid.
