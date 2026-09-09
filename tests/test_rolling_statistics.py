import numpy as np
import pandas as pd
import pytest

from ml.analysis.rolling import (
    rolling_mean_return,
    rolling_price_mean,
    rolling_return_std,
)


def test_rolling_statistics_use_trailing_windows() -> None:
    prices = pd.Series([100.0, 101.0, 102.0, 103.0])
    returns = pd.Series([np.nan, 0.01, 0.02, 0.03])

    price_mean = rolling_price_mean(prices, 2)
    return_mean = rolling_mean_return(returns, 2)
    return_std = rolling_return_std(returns, 2)

    assert np.isnan(price_mean.iloc[0])
    assert np.isclose(price_mean.iloc[1], 100.5)
    assert np.isnan(return_mean.iloc[1])
    assert np.isclose(return_mean.iloc[2], 0.015)
    assert np.isclose(return_std.iloc[2], np.std([0.01, 0.02], ddof=1))


@pytest.mark.parametrize("window", [0, -1, True, 1.5])
def test_rolling_statistics_reject_invalid_windows(window) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        rolling_price_mean(pd.Series([1.0]), window)