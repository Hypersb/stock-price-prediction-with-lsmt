import numpy as np
import pandas as pd

from ml.features.volatility import volatility_features


def test_volatility_features_are_trailing_and_optionally_annualized() -> None:
    close = pd.Series([100.0, 101.0, 103.0, 102.0])

    daily = volatility_features(close, [2])
    annualized = volatility_features(close, [2], periods_per_year=4)
    returns = close.pct_change(fill_method=None)
    expected = returns.rolling(2, min_periods=2).std()

    assert np.allclose(daily["volatility_2"], expected, equal_nan=True)
    assert np.allclose(annualized["volatility_2"], expected * 2, equal_nan=True)