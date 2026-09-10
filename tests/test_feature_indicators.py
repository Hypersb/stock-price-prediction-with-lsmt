import numpy as np
import pandas as pd

from ml.features.indicators import (
    average_true_range,
    macd_features,
    relative_strength_index,
)


def test_rsi_uses_wilder_smoothing_and_warmup() -> None:
    close = pd.Series(np.arange(1.0, 20.0))

    result = relative_strength_index(close, period=3)

    assert result.name == "rsi_3"
    assert result.iloc[:3].isna().all()
    assert np.isclose(result.iloc[-1], 100.0)


def test_macd_exposes_numeric_components() -> None:
    close = pd.Series(np.arange(1.0, 40.0))

    result = macd_features(close, fast=3, slow=5, signal=2)

    assert list(result.columns) == ["macd", "macd_signal", "macd_histogram"]
    assert np.isfinite(result["macd"].dropna()).all()
    assert np.allclose(result["macd_histogram"], result["macd"] - result["macd_signal"], equal_nan=True)


def test_atr_uses_true_range_and_wilder_smoothing() -> None:
    data = pd.DataFrame(
        {
            "high": [10.0, 12.0, 13.0, 15.0],
            "low": [8.0, 9.0, 11.0, 12.0],
            "close": [9.0, 11.0, 12.0, 14.0],
        }
    )

    result = average_true_range(data, period=2)

    true_range = pd.Series([2.0, 3.0, 2.0, 3.0])
    expected = true_range.ewm(alpha=0.5, adjust=False, min_periods=2).mean()
    assert np.allclose(result, expected, equal_nan=True)