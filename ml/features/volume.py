"""Trailing volume-derived features."""

import pandas as pd


def volume_features(volume: pd.Series, window: int = 20) -> pd.DataFrame:
    """Calculate volume change, lag, trailing mean, and relative volume."""
    if not isinstance(volume, pd.Series):
        raise TypeError("volume must be a pandas Series")
    if volume.isna().any() or (volume < 0).any():
        raise ValueError("volume values must be nonnegative and non-missing")
    if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
        raise ValueError("window must be a positive integer")
    average = volume.rolling(window=window, min_periods=window).mean()
    return pd.DataFrame(
        {
            "volume_change": volume.pct_change(fill_method=None),
            "volume_lag_1": volume.shift(1),
            f"volume_sma_{window}": average,
            f"relative_volume_{window}": volume / average,
        },
        index=volume.index,
    )