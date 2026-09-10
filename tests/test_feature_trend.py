import numpy as np
import pandas as pd

from ml.features.trend import moving_average_features


def test_moving_average_features_are_trailing() -> None:
    close = pd.Series([100.0, 102.0, 104.0, 106.0])

    result = moving_average_features(close, [2])

    assert np.isnan(result.loc[0, "sma_2"])
    assert np.isclose(result.loc[1, "sma_2"], 101.0)
    assert np.isclose(result.loc[2, "close_to_sma_2"], 104 / 103 - 1)
