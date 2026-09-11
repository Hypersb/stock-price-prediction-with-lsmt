# Final Quantitative Research Report

## 1. Executive Summary

_Awaiting generated results from a legitimate executed experiment._

This report must be able to conclude that the LSTM did not consistently
outperform simpler models when that is what the evidence shows. Promotional
conclusions unsupported by evidence are not permitted.

Generate a populated report programmatically with:

```python
from ml.research.report import render_final_research_report
from ml.research.pipeline import run_final_research_evaluation

# result = run_final_research_evaluation(market_data, config)
# document = render_final_research_report(result)
document = render_final_research_report(None)
print(document.markdown)
```

## 2. Research Question

Does an LSTM forecasting model improve out-of-sample predictive and economic
performance relative to naive, linear/logistic, and tree baselines under
leakage-safe chronological evaluation?

## 3. Dataset

_Awaiting generated results from a legitimate executed experiment._

## 4. Feature Engineering

See [research-methodology.md](research-methodology.md). Features include lagged
returns, momentum, moving averages, EMA ratios, rolling volatility, volume
features, RSI, MACD, and ATR, with leakage validation.

## 5. Prediction Targets

Future-return regression and/or direction classification at a configured
horizon. Targets are constructed separately from features.

## 6. Models

Naive, linear/logistic, random forest, gradient boosting, and LSTM families
evaluated under comparable methodology.

## 7. Validation Methodology

Chronological splits, expanding/rolling walk-forward folds, temporal purging,
train-only fold preprocessing, and true out-of-sample prediction collection.

## 8. Multi-Asset Results

_Awaiting generated results from a legitimate executed experiment._

## 9. Regime Results

_Awaiting generated results from a legitimate executed experiment._

## 10. Feature Importance

_Awaiting generated results from a legitimate executed experiment._

## 11. Ablation Results

_Awaiting generated results from a legitimate executed experiment._

## 12. Model Complexity

_Awaiting generated results from a legitimate executed experiment._

## 13. Statistical Comparison

_Awaiting generated results from a legitimate executed experiment._

## 14. Backtesting Results

_Awaiting generated results from a legitimate executed experiment._

## 15. Cost Sensitivity

_Awaiting generated results from a legitimate executed experiment._

## 16. Limitations

- Historical Yahoo Finance research data has survivorship and revision limits.
- Regime labels are rule-based diagnostics, not causal regime discovery.
- Permutation/LSTM sensitivity is not causal feature attribution.
- Local timings are environment-dependent diagnostics.
- Transaction-cost assumptions are research scenarios, not live brokerage costs.
- No live trading, portfolio execution, or profitability guarantee is claimed.

## 17. Conclusions

_Awaiting generated results from a legitimate executed experiment._

A valid conclusion includes: **the evidence does not demonstrate that the LSTM
consistently outperforms simpler models.**

## 18. Future Work

Licensed real-time feeds, news/NLP sentiment, Transformer sequence models,
portfolio optimization, multi-asset allocation, paper trading, and model
monitoring remain future extensions and are not implemented in this phase.
