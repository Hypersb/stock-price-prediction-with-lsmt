import numpy as np
import pandas as pd
import pytest

from ml.features.momentum import momentum_features


def test_momentum_uses_trailing_close_values() -> None:
    close = pd.Series([100.0, 110.0, 121.0], index=pd.date_range("2020-01-01", periods=3))

    result = momentum_features(close, [1, 2])

    assert np.isnan(result.iloc[0, 0])
    assert np.isclose(result.iloc[1, 0], 0.1)
    assert np.isclose(result.iloc[2, 1], 0.21)


@pytest.mark.parametrize("windows", [[0], [-1], [True], [1, 1]])
def test_momentum_rejects_invalid_windows(windows) -> None:
    with pytest.raises(ValueError):
        momentum_features(pd.Series([100.0]), windows)


def test_momentum_rejects_nonpositive_close() -> None:
    with pytest.raises(ValueError, match="positive"):
        momentum_features(pd.Series([100.0, 0.0]), [1])