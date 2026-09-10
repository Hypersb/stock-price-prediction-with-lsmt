import numpy as np
import pandas as pd
import pytest

from ml.features.volume import volume_features


def test_volume_features_use_trailing_information() -> None:
    volume = pd.Series([100.0, 200.0, 300.0, 400.0])

    result = volume_features(volume, window=2)

    assert np.isnan(result.loc[0, "volume_change"])
    assert result.loc[2, "volume_lag_1"] == 200.0
    assert result.loc[2, "volume_sma_2"] == 250.0
    assert result.loc[2, "relative_volume_2"] == 1.2


def test_volume_features_reject_negative_volume_and_invalid_window() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        volume_features(pd.Series([100.0, -1.0]))
    with pytest.raises(ValueError, match="positive integer"):
        volume_features(pd.Series([100.0]), window=0)