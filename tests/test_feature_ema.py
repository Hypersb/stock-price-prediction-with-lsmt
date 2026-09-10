import numpy as np
import pandas as pd

from ml.features.ema import exponential_moving_average_features


def test_ema_uses_adjust_false_convention_and_warmup() -> None:
    close = pd.Series([100.0, 102.0, 104.0, 106.0])

    result = exponential_moving_average_features(close, [2])

    expected = close.ewm(span=2, adjust=False, min_periods=2).mean()
    assert np.allclose(result["ema_2"], expected, equal_nan=True)
    assert np.isclose(result.loc[2, "close_to_ema_2"], close.loc[2] / expected.loc[2] - 1)