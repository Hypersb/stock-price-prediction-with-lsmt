import numpy as np
import pandas as pd

from ml.backtesting.returns import calculate_strategy_returns


def test_strategy_returns_compound_net_returns_and_preserve_costs() -> None:
    result = calculate_strategy_returns(
        pd.Series([1.0, 1.0]),
        pd.Series([0.10, -0.10]),
        initial_capital=100.0,
    )

    assert np.isclose(result["equity"].iloc[-1], 99.0)
    assert np.isclose(result["net_strategy_return"].sum(), 0.0)
    assert result["trading_cost"].tolist() == [0.0, 0.0]