"""Compounded cumulative return calculations."""

import pandas as pd


def cumulative_returns(returns: pd.Series) -> pd.Series:
    """Calculate $R_t = product(1 + r_i) - 1$ from a return series."""
    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a pandas Series")
    return (1 + returns).cumprod() - 1