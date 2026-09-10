import numpy as np
import pandas as pd

from ml.backtesting.metrics import calculate_metrics


def test_metrics_calculate_compounded_return_and_drawdown() -> None:
    metrics = calculate_metrics(pd.Series([0.10, -0.10]))

    assert np.isclose(metrics["total_return"], -0.01)
    assert np.isclose(metrics["maximum_drawdown"], -0.10)
    assert metrics["hit_rate"] == 0.5


def test_zero_volatility_sharpe_is_safe() -> None:
    metrics = calculate_metrics(pd.Series([0.0, 0.0]))

    assert metrics["annualized_volatility"] == 0.0
    assert metrics["sharpe_ratio"] == 0.0