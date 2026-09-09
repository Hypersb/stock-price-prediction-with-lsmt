"""Historical rolling volatility calculations."""

import math

import pandas as pd

from ml.analysis.rolling import rolling_return_std


def daily_rolling_volatility(returns: pd.Series, window: int) -> pd.Series:
    """Calculate trailing daily sample volatility from returns."""
    return rolling_return_std(returns, window).rename("daily_volatility")


def annualized_rolling_volatility(
    returns: pd.Series,
    window: int,
    periods_per_year: float = 252,
) -> pd.Series:
    """Annualize daily volatility using sqrt(periods_per_year).

    252 is the conventional approximate number of trading days per year.
    Volatility describes historical dispersion and does not predict returns.
    """
    if isinstance(periods_per_year, bool) or periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")
    daily = daily_rolling_volatility(returns, window)
    return (daily * math.sqrt(periods_per_year)).rename("annualized_volatility")