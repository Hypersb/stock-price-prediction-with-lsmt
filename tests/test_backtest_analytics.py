import pandas as pd

from ml.backtesting.analytics import strategy_analytics


def test_strategy_analytics_reports_exposure_turnover_and_trades() -> None:
    analytics = strategy_analytics(pd.Series([0, 1, 1, -1, 0], dtype=float), pd.Series([0.0, 0.1, -0.02, -0.1, 0.0]))

    assert analytics["total_turnover"] == 4.0
    assert analytics["position_changes"] == 3
    assert analytics["long_exposure"] == 0.4
    assert analytics["short_exposure"] == 0.2
    assert analytics["completed_trades"] == 2