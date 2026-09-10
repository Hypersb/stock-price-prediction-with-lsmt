import pandas as pd

from ml.backtesting.benchmark import compare_buy_and_hold


def test_benchmark_requires_matching_dates_and_returns_metrics() -> None:
    dates = pd.date_range("2020-01-02", periods=2)
    strategy = pd.DataFrame({"realization_date": dates, "net_strategy_return": [0.1, -0.1]})
    underlying = pd.DataFrame({"date": dates, "realized_return": [0.1, -0.1]})

    result = compare_buy_and_hold(strategy, underlying)

    assert result["strategy"]["total_return"] == result["buy_and_hold"]["total_return"]