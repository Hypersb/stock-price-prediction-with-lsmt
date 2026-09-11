# Final Quantitative Research Report

This document separates **what the platform implements** from **what has been
empirically executed**. Do not treat capability descriptions as measured
results. Sections marked _Awaiting…_ must stay empty until a legitimate
experiment is run and rendered.

Generate a populated report programmatically with:

```python
from ml.research.report import render_final_research_report
from ml.research.pipeline import run_final_research_evaluation

# result = run_final_research_evaluation(market_data, config)
# document = render_final_research_report(result)
document = render_final_research_report(None)
print(document.markdown)
```

---

## Implemented Capability (platform)

These items describe software that exists in the repository. They are **not**
empirical performance claims.

| Area | Capability |
|------|------------|
| Data | Historical OHLCV via provider abstraction; validation/normalization |
| Features | Leakage-aware feature engineering with quality checks |
| Targets | Future-return regression; binary direction (`1` if `future_return > 0` else `0` when defined; NaN stays missing) |
| Models | Naive, linear/logistic, random forest, gradient boosting, PyTorch LSTM |
| LSTM sequences | Lookback windows; prior within-fold features may supply context only |
| Validation | Chronological splits; expanding/rolling walk-forward with purging |
| OOS | True out-of-sample prediction collection and PostgreSQL persistence |
| Evaluation | Regression/classification metrics; multi-asset robustness utilities |
| Diagnostics | Regimes, explainability, ablation, complexity, block-bootstrap comparison |
| Backtesting | OOS signals, `forecast_horizon=1` execution alignment, costs/slippage, fold-aware stitching |
| Sensitivity | Diagnostic cost/threshold sweeps (no holdout cherry-picking for claims) |
| Orchestration | `ml/research/pipeline.py` + config fingerprints + report renderer |
| Serving | FastAPI `/api/v1`, PostgreSQL, Next.js dashboard reading persisted artifacts |

---

## Empirically Executed Result (awaiting)

Populate only after a real run. Until then, keep awaiting placeholders.

### 1. Executive Summary

_Awaiting generated results from a legitimate executed experiment._

This report must be able to conclude that the LSTM did not consistently
outperform simpler models when that is what the evidence shows. Promotional
conclusions unsupported by evidence are not permitted.

### 2. Research Question

Does an LSTM forecasting model improve out-of-sample predictive and economic
performance relative to naive, linear/logistic, and tree baselines under
leakage-safe chronological evaluation?

### 3. Dataset

_Awaiting generated results from a legitimate executed experiment._

### 4. Feature Engineering

See [research-methodology.md](research-methodology.md). Features include lagged
returns, momentum, moving averages, EMA ratios, rolling volatility, volume
features, RSI, MACD, and ATR, with leakage validation.

### 5. Prediction Targets

Future-return regression and/or direction classification at a configured
horizon. Targets are constructed separately from features. Direction semantics:
up (`1`) iff defined `future_return > 0`; otherwise `0`; missing stays NA.

### 6. Models

Naive, linear/logistic, random forest, gradient boosting, and LSTM families
evaluated under comparable methodology.

### 7. Validation Methodology

Chronological splits, expanding/rolling walk-forward folds, temporal purging,
train-only fold preprocessing, context-aware LSTM sequences, and true
out-of-sample prediction collection.

### 8. Multi-Asset Results

_Awaiting generated results from a legitimate executed experiment._

### 9. Regime Results

_Awaiting generated results from a legitimate executed experiment._

### 10. Feature Importance

_Awaiting generated results from a legitimate executed experiment._

### 11. Ablation Results

_Awaiting generated results from a legitimate executed experiment._

### 12. Model Complexity

_Awaiting generated results from a legitimate executed experiment._

### 13. Statistical Comparison

_Awaiting generated results from a legitimate executed experiment._

### 14. Backtesting Results

_Awaiting generated results from a legitimate executed experiment._

Strategy backtests in this platform require `forecast_horizon=1`. Fold-aware
stitching rejects overlapping OOS dates and does not continuous-annualize across
gaps.

### 15. Cost Sensitivity

_Awaiting generated results from a legitimate executed experiment._

### 16. Limitations

- Historical Yahoo Finance research data has survivorship and revision limits.
- Regime labels are rule-based diagnostics, not causal regime discovery.
- Permutation/LSTM sensitivity is not causal feature attribution.
- Local timings are environment-dependent diagnostics.
- Transaction-cost assumptions are research scenarios, not live brokerage costs.
- No live trading, portfolio execution, or profitability guarantee is claimed.
- Implemented capability must not be confused with executed empirical results.

### 17. Conclusions

_Awaiting generated results from a legitimate executed experiment._

A valid conclusion includes: **the evidence does not demonstrate that the LSTM
consistently outperforms simpler models.**

### 18. Future Work

Licensed real-time feeds, news/NLP sentiment, Transformer sequence models,
portfolio optimization, multi-asset allocation, paper trading, and model
monitoring remain future extensions and are not implemented in this phase.
