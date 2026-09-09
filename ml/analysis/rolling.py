"""Trailing rolling statistics for prices and returns."""

import pandas as pd


def rolling_price_mean(prices: pd.Series, window: int) -> pd.Series:
    """Calculate a trailing rolling mean of prices."""
    _validate_window(window)
    return prices.rolling(window=window, min_periods=window).mean().rename("rolling_price_mean")


def rolling_mean_return(returns: pd.Series, window: int) -> pd.Series:
    """Calculate a trailing rolling mean of returns."""
    _validate_window(window)
    return returns.rolling(window=window, min_periods=window).mean().rename("rolling_mean_return")


def rolling_return_std(returns: pd.Series, window: int) -> pd.Series:
    """Calculate a trailing rolling sample standard deviation of returns."""
    _validate_window(window)
    return returns.rolling(window=window, min_periods=window).std().rename("rolling_return_std")


def _validate_window(window: int) -> None:
    if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
        raise ValueError("rolling window must be a positive integer")