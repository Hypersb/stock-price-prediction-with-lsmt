"""End-to-end historical research backtest orchestration."""

from dataclasses import dataclass

import pandas as pd

from ml.backtesting.analytics import strategy_analytics
from ml.backtesting.benchmark import compare_buy_and_hold
from ml.backtesting.config import BacktestConfig
from ml.backtesting.costs import calculate_turnover
from ml.backtesting.execution import align_execution
from ml.backtesting.metrics import calculate_metrics
from ml.backtesting.returns import calculate_strategy_returns
from ml.backtesting.signals import prediction_signals


@dataclass(frozen=True)
class BacktestResult:
    """Serializable-enough historical simulation output."""

    configuration: BacktestConfig
    model: str
    task: str
    observations: int
    timeline: pd.DataFrame
    metrics: dict[str, float]
    analytics: dict[str, float | int]
    benchmark: dict[str, dict[str, float]]


def run_backtest(
    out_of_sample_predictions: pd.DataFrame,
    market_returns: pd.DataFrame,
    config: BacktestConfig,
) -> BacktestResult:
    """Run a prediction-driven historical simulation on out-of-sample records."""
    if out_of_sample_predictions.empty:
        raise ValueError("out_of_sample_predictions must not be empty")
    signals = prediction_signals(out_of_sample_predictions, config)
    aligned = align_execution(signals, market_returns)
    if aligned.empty:
        raise ValueError("predictions have no subsequent realized return")
    positions = aligned["signal"].astype(float)
    strategy = calculate_strategy_returns(
        positions,
        aligned["realized_return"],
        transaction_cost_bps=config.transaction_cost_bps,
        slippage_bps=config.slippage_bps,
        initial_capital=config.initial_capital,
    )
    timeline = pd.concat(
        [aligned.reset_index(drop=True), strategy.reset_index(drop=True)], axis=1
    )
    timeline["turnover"] = calculate_turnover(timeline["position"])
    metrics = calculate_metrics(
        timeline["net_strategy_return"],
        annualization_factor=config.annualization_factor,
    )
    analytics = strategy_analytics(timeline["position"], timeline["net_strategy_return"])
    benchmark = compare_buy_and_hold(
        timeline,
        market_returns.loc[
            market_returns["date"].isin(timeline["realization_date"])
        ].copy(),
        annualization_factor=config.annualization_factor,
    )
    return BacktestResult(
        configuration=config,
        model=str(out_of_sample_predictions["model"].iloc[0]),
        task=str(out_of_sample_predictions["task"].iloc[0]),
        observations=len(timeline),
        timeline=timeline,
        metrics=metrics,
        analytics=analytics,
        benchmark=benchmark,
    )