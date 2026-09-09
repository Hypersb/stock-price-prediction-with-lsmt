import numpy as np
import pandas as pd

from ml.analysis.returns import log_returns, simple_returns


def prices() -> pd.DataFrame:
    return pd.DataFrame({"close": [100.0, 110.0, 99.0]})


def test_simple_returns_use_close_and_preserve_first_missing_value() -> None:
    data = prices()

    result = simple_returns(data)

    assert np.isnan(result.iloc[0])
    assert result.iloc[1] == 0.1
    assert result.iloc[2] == -0.1
    assert list(data.columns) == ["close"]


def test_log_returns_use_log_price_ratio() -> None:
    result = log_returns(prices())

    assert np.isnan(result.iloc[0])
    assert np.isclose(result.iloc[1], np.log(1.1))
    assert np.isclose(result.iloc[2], np.log(0.9))