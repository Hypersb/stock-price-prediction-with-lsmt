"""Trailing price momentum features."""

from collections.abc import Iterable

import pandas as pd


def momentum_features(
    close: pd.Series,
    windows: Iterable[int],
) -> pd.DataFrame:
    """Calculate $close_t / close_{t-k} - 1$ for trailing horizons."""
    if not isinstance(close, pd.Series):
        raise TypeError("close must be a pandas Series")
    if close.isna().any() or (close <= 0).any():
        raise ValueError("close values must be positive and non-missing")
    normalized_windows = _validate_windows(windows)
    return pd.DataFrame(
        {f"momentum_{window}": close / close.shift(window) - 1 for window in normalized_windows},
        index=close.index,
    )


def _validate_windows(windows: Iterable[int]) -> tuple[int, ...]:
    normalized = tuple(windows)
    if any(isinstance(window, bool) or not isinstance(window, int) or window <= 0 for window in normalized):
        raise ValueError("windows must contain positive integers")
    if len(set(normalized)) != len(normalized):
        raise ValueError("windows must not contain duplicates")
    return normalized