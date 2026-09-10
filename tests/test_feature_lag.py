import numpy as np
import pandas as pd
import pytest

from ml.features.lag import lagged_returns


def test_lagged_returns_use_only_previous_observations() -> None:
    returns = pd.Series([0.01, 0.02, 0.03], index=pd.date_range("2020-01-01", periods=3))

    result = lagged_returns(returns, [1, 2])

    assert np.isnan(result.loc[returns.index[0], "return_lag_1"])
    assert result.loc[returns.index[1], "return_lag_1"] == 0.01
    assert result.loc[returns.index[2], "return_lag_2"] == 0.01


@pytest.mark.parametrize("lags", [[0], [-1], [True], [1, 1]])
def test_lagged_returns_reject_invalid_lags(lags) -> None:
    with pytest.raises(ValueError):
        lagged_returns(pd.Series([0.01]), lags)