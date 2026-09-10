"""Trailing simple and exponential trend features."""

from collections.abc import Iterable

import pandas as pd


def moving_average_features(close: pd.Series, windows: Iterable[int]) -> pd.DataFrame:
    """Calculate trailing SMA and relative close-to-SMA features."""
    _validate_close(close)
    normalized_windows = _validate_windows(windows)
    result: dict[str, pd.Series] = {}
    for window in normalized_windows:
        sma = close.rolling(window=window, min_periods=window).mean()
        result[f"sma_{window}"] = sma
        result[f"close_to_sma_{window}"] = close / sma - 1
    return pd.DataFrame(result, index=close.index)


def _validate_close(close: pd.Series) -> None:
    if not isinstance(close, pd.Series):
        raise TypeError("close must be a pandas Series")
    if close.isna().any() or (close <= 0).any():
        raise ValueError("close values must be positive and non-missing")


def _validate_windows(windows: Iterable[int]) -> tuple[int, ...]:
    normalized = tuple(windows)
    if any(isinstance(window, bool) or not isinstance(window, int) or window <= 0 for window in normalized):
        raise ValueError("windows must contain positive integers")
    if len(set(normalized)) != len(normalized):
        raise ValueError("windows must not contain duplicates")
    return normalized