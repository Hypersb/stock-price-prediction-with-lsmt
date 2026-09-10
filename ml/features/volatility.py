"""Historical volatility features for machine-learning inputs."""

from collections.abc import Iterable

import pandas as pd

from ml.analysis.returns import simple_returns
from ml.analysis.rolling import rolling_return_std


def volatility_features(
    close: pd.Series,
    windows: Iterable[int],
    periods_per_year: float | None = None,
) -> pd.DataFrame:
    """Calculate trailing return volatility, optionally annualized.

    Volatility uses sample standard deviation of close-to-close simple returns.
    If ``periods_per_year`` is provided, each result is annualized by its square
    root; 252 is the conventional approximate trading-day value.
    """
    if not isinstance(close, pd.Series):
        raise TypeError("close must be a pandas Series")
    if close.isna().any() or (close <= 0).any():
        raise ValueError("close values must be positive and non-missing")
    if periods_per_year is not None and (
        isinstance(periods_per_year, bool) or periods_per_year <= 0
    ):
        raise ValueError("periods_per_year must be positive")
    normalized_windows = _validate_windows(windows)
    returns = simple_returns(pd.DataFrame({"close": close}))
    result = {
        f"volatility_{window}": rolling_return_std(returns, window)
        for window in normalized_windows
    }
    if periods_per_year is not None:
        multiplier = periods_per_year**0.5
        result = {name: values * multiplier for name, values in result.items()}
    return pd.DataFrame(result, index=close.index)


def _validate_windows(windows: Iterable[int]) -> tuple[int, ...]:
    normalized = tuple(windows)
    if any(isinstance(window, bool) or not isinstance(window, int) or window <= 0 for window in normalized):
        raise ValueError("windows must contain positive integers")
    if len(set(normalized)) != len(normalized):
        raise ValueError("windows must not contain duplicates")
    return normalized