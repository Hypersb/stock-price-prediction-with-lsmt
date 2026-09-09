"""Simple and logarithmic return calculations."""

import numpy as np
import pandas as pd


def simple_returns(data: pd.DataFrame, price_column: str = "close") -> pd.Series:
    """Calculate $r_t = P_t / P_(t-1) - 1$ from closing prices."""
    prices = _prices(data, price_column)
    return prices.pct_change(fill_method=None).rename("simple_return")


def log_returns(data: pd.DataFrame, price_column: str = "close") -> pd.Series:
    """Calculate $log_return_t = ln(P_t / P_(t-1))$ from closing prices."""
    prices = _prices(data, price_column)
    if (prices.dropna() <= 0).any():
        raise ValueError("prices must be positive for logarithmic returns")
    return np.log(prices / prices.shift(1)).rename("log_return")


def _prices(data: pd.DataFrame, price_column: str) -> pd.Series:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("market data must be a pandas DataFrame")
    if price_column not in data.columns:
        raise ValueError(f"market data is missing price column: {price_column}")
    return data[price_column].copy()