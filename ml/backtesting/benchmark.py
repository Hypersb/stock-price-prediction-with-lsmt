"""Same-period buy-and-hold benchmark comparison."""

import pandas as pd

from ml.backtesting.metrics import calculate_metrics


def compare_buy_and_hold(
    strategy: pd.DataFrame,
    underlying_returns: pd.DataFrame | pd.Series,
    *,
    annualization_factor: float = 252,
) -> dict[str, dict[str, float]]:
    """Compare strategy net returns with buy-and-hold on exactly matching dates."""
    if "realization_date" not in strategy.columns or "net_strategy_return" not in strategy.columns:
        raise ValueError("strategy must contain realization_date and net_strategy_return")
    if isinstance(underlying_returns, pd.Series):
        benchmark = underlying_returns.rename("benchmark_return").to_frame()
        benchmark.index = pd.to_datetime(benchmark.index)
    else:
        if not {"date", "realized_return"}.issubset(underlying_returns.columns):
            raise ValueError("underlying returns require date and realized_return")
        benchmark = underlying_returns.set_index("date")["realized_return"].rename("benchmark_return").to_frame()
        benchmark.index = pd.to_datetime(benchmark.index)
    strategy_dates = pd.DatetimeIndex(pd.to_datetime(strategy["realization_date"]))
    if set(strategy_dates) != set(benchmark.index):
        raise ValueError("strategy and benchmark dates must match exactly")
    benchmark = benchmark.loc[strategy_dates]
    return {
        "strategy": calculate_metrics(strategy["net_strategy_return"], annualization_factor=annualization_factor),
        "buy_and_hold": calculate_metrics(benchmark["benchmark_return"], annualization_factor=annualization_factor),
    }