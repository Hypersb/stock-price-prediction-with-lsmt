"""Future-return regression target construction."""

from collections.abc import Iterable

import pandas as pd


def future_return_targets(
    close: pd.Series,
    horizons: Iterable[int],
) -> pd.DataFrame:
    """Calculate $close_{t+h} / close_t - 1$ for positive horizons."""
    if not isinstance(close, pd.Series):
        raise TypeError("close must be a pandas Series")
    if close.isna().any() or (close <= 0).any():
        raise ValueError("close values must be positive and non-missing")
    normalized_horizons = _validate_horizons(horizons)
    return pd.DataFrame(
        {
            f"future_return_{horizon}": close.shift(-horizon) / close - 1
            for horizon in normalized_horizons
        },
        index=close.index,
    )


def _validate_horizons(horizons: Iterable[int]) -> tuple[int, ...]:
    normalized = tuple(horizons)
    if any(
        isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0
        for horizon in normalized
    ):
        raise ValueError("horizons must contain positive integers")
    if len(set(normalized)) != len(normalized):
        raise ValueError("horizons must not contain duplicates")
    return normalized