"""Render structured final-research results into markdown report sections.

Does not fabricate experimental numbers. Missing executed results are marked as
awaiting generated results.
"""

from __future__ import annotations

from dataclasses import dataclass

from ml.research.pipeline import FinalResearchResult


@dataclass(frozen=True)
class ResearchReportDocument:
    """Markdown report body and metadata."""

    title: str
    experiment_id: str | None
    markdown: str
    populated_from_results: bool


def render_final_research_report(
    result: FinalResearchResult | None = None,
) -> ResearchReportDocument:
    """Create the final research report markdown.

    If ``result`` is None, result sections are explicitly marked as awaiting
    generated results rather than filled with invented numbers.
    """
    if result is None:
        markdown = _template_awaiting_results()
        return ResearchReportDocument(
            title="Final Quantitative Research Report",
            experiment_id=None,
            markdown=markdown,
            populated_from_results=False,
        )
    markdown = _template_with_results(result)
    return ResearchReportDocument(
        title="Final Quantitative Research Report",
        experiment_id=result.experiment_id,
        markdown=markdown,
        populated_from_results=True,
    )


def _template_awaiting_results() -> str:
    awaiting = "_Awaiting generated results from a legitimate executed experiment._"
    return f"""# Final Quantitative Research Report

## 1. Executive Summary

{awaiting}

This report must be able to conclude that the LSTM did not consistently
outperform simpler models when that is what the evidence shows. Promotional
conclusions unsupported by evidence are not permitted.

## 2. Research Question

Does an LSTM forecasting model improve out-of-sample predictive and economic
performance relative to naive, linear/logistic, and tree baselines under
leakage-safe chronological evaluation?

## 3. Dataset

{awaiting}

## 4. Feature Engineering

See `docs/research-methodology.md`. Features include lagged returns, momentum,
moving averages, EMA ratios, rolling volatility, volume features, RSI, MACD,
and ATR, with leakage validation.

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

{awaiting}

## 9. Regime Results

{awaiting}

## 10. Feature Importance

{awaiting}

## 11. Ablation Results

{awaiting}

## 12. Model Complexity

{awaiting}

## 13. Statistical Comparison

{awaiting}

## 14. Backtesting Results

{awaiting}

## 15. Cost Sensitivity

{awaiting}

## 16. Limitations

- Historical Yahoo Finance research data has survivorship and revision limits.
- Regime labels are rule-based diagnostics, not causal regime discovery.
- Permutation/LSTM sensitivity is not causal feature attribution.
- Local timings are environment-dependent diagnostics.
- Transaction-cost assumptions are research scenarios, not live brokerage costs.
- No live trading, portfolio execution, or profitability guarantee is claimed.

## 17. Conclusions

{awaiting}

A valid conclusion includes: the evidence does not demonstrate that the LSTM
consistently outperforms simpler models.

## 18. Future Work

Licensed real-time feeds, news/NLP sentiment, Transformer sequence models,
portfolio optimization, multi-asset allocation, paper trading, and model
monitoring remain future extensions and are not implemented in this phase.
"""


def _template_with_results(result: FinalResearchResult) -> str:
    summary_table = result.multi_asset.summary_table()
    multi_asset_md = (
        summary_table.to_markdown(index=False)
        if not summary_table.empty
        else "_No multi-asset rows were produced._"
    )
    regime_lines = [
        (
            f"- {item.dimension}/{item.regime}/{item.model}: "
            f"n={item.observations}, interpretable={item.interpretable}, "
            f"metrics={item.metrics}"
        )
        for item in result.regime_results[:50]
    ] or ["_No regime metric rows._"]
    ablation_lines = [
        (
            f"- {item.experiment}: features={item.feature_count}, "
            f"abs_change={item.absolute_change}"
        )
        for item in result.ablation_results
    ] or ["_No ablation rows._"]
    complexity_lines = []
    if result.complexity is not None:
        for row in result.complexity.rows:
            complexity_lines.append(
                f"- {row.model_name}: params={row.parameter_count}, "
                f"train_s={row.training_seconds:.4f}, metrics={row.metrics}"
            )
    else:
        complexity_lines = ["_Complexity comparison not requested._"]
    stats_lines = [
        (
            f"- {item.model_a} vs {item.model_b} ({item.metric}): "
            f"diff={item.observed_difference:.6f}, "
            f"CI={item.confidence_interval}, n={item.observations}"
        )
        for item in result.statistical_comparisons
    ] or ["_No statistical comparisons._"]
    backtest_lines = [
        (
            f"- {symbol}/{model}: total_return={backtest.metrics.get('total_return')}, "
            f"sharpe={backtest.metrics.get('sharpe_ratio')}, "
            f"max_dd={backtest.metrics.get('maximum_drawdown')}"
        )
        for symbol, model, backtest in result.backtests
    ] or ["_No backtests produced._"]
    sensitivity_lines = []
    for symbol, model, sensitivity in result.sensitivity:
        sensitivity_lines.append(f"- {symbol}/{model}:")
        for row in sensitivity.rows:
            sensitivity_lines.append(
                f"  - {row.configuration}: net={row.net_return:.6f}, "
                f"sharpe={row.sharpe:.4f}, turnover={row.turnover:.4f}"
            )
    if not sensitivity_lines:
        sensitivity_lines = ["_No sensitivity rows._"]

    return f"""# Final Quantitative Research Report

Experiment id: `{result.experiment_id}`

## 1. Executive Summary

Structured results were generated from configuration fingerprint
`{result.experiment_id}`. Interpret numbers only in the context of the stated
assumptions. If the LSTM does not beat simpler baselines, that is a valid
scientific outcome.

## 2. Research Question

Does an LSTM improve out-of-sample predictive and economic performance versus
naive, linear/logistic, and tree baselines under leakage-safe chronological
evaluation?

## 3. Dataset

Symbols evaluated: {", ".join(result.configuration.symbols)}.
Target type: `{result.configuration.target_type}`; horizon: `{result.configuration.horizon}`.

## 4. Feature Engineering

Feature parameters: `{result.configuration.feature_parameters}`.

## 5. Prediction Targets

Configured target type `{result.configuration.target_type}` at horizon
`{result.configuration.horizon}`.

## 6. Models

Families: {", ".join(result.configuration.model_families)}.

## 7. Validation Methodology

Walk-forward: `{result.configuration.walk_forward}`.

## 8. Multi-Asset Results

{multi_asset_md}

## 9. Regime Results

{chr(10).join(regime_lines)}

## 10. Feature Importance

{chr(10).join(f"- {item.model_name}/{item.method}: top={item.importances[:5]}" for item in result.explainability) or "_Explainability not requested or unavailable._"}

## 11. Ablation Results

{chr(10).join(ablation_lines)}

## 12. Model Complexity

{chr(10).join(complexity_lines)}

## 13. Statistical Comparison

{chr(10).join(stats_lines)}

## 14. Backtesting Results

{chr(10).join(backtest_lines)}

## 15. Cost Sensitivity

{chr(10).join(sensitivity_lines)}

## 16. Limitations

- Results depend on configured costs, thresholds, seeds, and universe choices.
- Regime labels and permutation sensitivities are diagnostic, not causal proof.
- No claim of live profitability is made.

## 17. Conclusions

Review the multi-asset, statistical, and cost-sensitivity sections before
claiming LSTM superiority. Absence of consistent outperformance is a valid
conclusion.

## 18. Future Work

Real-time feeds, NLP sentiment, Transformers, portfolio optimization, paper
trading, and monitoring remain future work.
"""
