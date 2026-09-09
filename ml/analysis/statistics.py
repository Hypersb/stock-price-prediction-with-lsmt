"""Descriptive statistics for market returns."""

import pandas as pd


def return_statistics(returns: pd.Series) -> pd.Series:
    """Return descriptive statistics after excluding missing observations.

    ``skewness`` and ``kurtosis`` use pandas Series conventions. In particular,
    pandas kurtosis is unbiased Fisher kurtosis, so a normal sample approaches
    zero excess kurtosis.
    """
    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a pandas Series")
    observed = returns.dropna()
    if observed.empty:
        raise ValueError("returns must contain at least one observed value")
    return pd.Series(
        {
            "count": observed.count(),
            "mean": observed.mean(),
            "median": observed.median(),
            "std": observed.std(),
            "min": observed.min(),
            "max": observed.max(),
            "skewness": observed.skew(),
            "kurtosis": observed.kurt(),
        }
    )