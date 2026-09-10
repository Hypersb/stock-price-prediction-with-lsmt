"""Lagged return feature calculations."""

from collections.abc import Iterable

import pandas as pd


def lagged_returns(returns: pd.Series, lags: Iterable[int]) -> pd.DataFrame:
    """Create positive trailing return lags without using future observations."""
    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a pandas Series")
    normalized_lags = _validate_lags(lags)
    return pd.DataFrame(
        {f"return_lag_{lag}": returns.shift(lag) for lag in normalized_lags},
        index=returns.index,
    )


def _validate_lags(lags: Iterable[int]) -> tuple[int, ...]:
    normalized = tuple(lags)
    if any(isinstance(lag, bool) or not isinstance(lag, int) or lag <= 0 for lag in normalized):
        raise ValueError("lags must contain positive integers")
    if len(set(normalized)) != len(normalized):
        raise ValueError("lags must not contain duplicates")
    return normalized