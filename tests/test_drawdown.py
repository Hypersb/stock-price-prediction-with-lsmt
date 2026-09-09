import numpy as np
import pandas as pd
import pytest

from ml.analysis.drawdown import (
    drawdown_series,
    maximum_drawdown,
    running_peak,
    wealth_index,
)


def test_rising_prices_have_no_drawdown() -> None:
    returns = pd.Series([np.nan, 0.1, 0.1])

    assert np.allclose(wealth_index(returns), [1.0, 1.1, 1.21])
    assert maximum_drawdown(returns) == 0.0


def test_drawdown_and_recovery_are_compounded_correctly() -> None:
    returns = pd.Series([np.nan, 0.1, -0.2, 0.25])

    wealth = wealth_index(returns)
    drawdowns = drawdown_series(returns)

    assert np.allclose(wealth, [1.0, 1.1, 0.88, 1.1])
    assert np.allclose(running_peak(wealth), [1.0, 1.1, 1.1, 1.1])
    assert np.allclose(drawdowns, [0.0, 0.0, -0.2, 0.0])
    assert np.isclose(maximum_drawdown(returns), -0.2)


def test_later_missing_returns_are_not_filled() -> None:
    with pytest.raises(ValueError, match="after the first value"):
        wealth_index(pd.Series([np.nan, 0.1, np.nan]))