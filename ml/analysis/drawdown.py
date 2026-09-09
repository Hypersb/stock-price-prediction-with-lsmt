"""Compounded wealth and drawdown analysis."""

import pandas as pd


def wealth_index(returns: pd.Series, initial_value: float = 1.0) -> pd.Series:
    """Build a compounded wealth index from returns.

    The first missing return represents the starting observation and is treated
    as zero. Missing returns after that point are rejected rather than filled.
    """
    clean_returns = _returns_for_wealth(returns)
    return (1 + clean_returns).cumprod().mul(initial_value).rename("wealth")


def running_peak(wealth: pd.Series) -> pd.Series:
    """Calculate the running high-water mark of a wealth series."""
    return wealth.cummax().rename("running_peak")


def drawdown_series(returns: pd.Series) -> pd.Series:
    """Calculate $DD_t = Wealth_t / RunningPeak_t - 1$."""
    wealth = wealth_index(returns)
    return (wealth / running_peak(wealth) - 1).rename("drawdown")


def maximum_drawdown(returns: pd.Series) -> float:
    """Return $MDD = min(DD_t)$ for a return series."""
    return float(drawdown_series(returns).min())


def _returns_for_wealth(returns: pd.Series) -> pd.Series:
    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a pandas Series")
    if returns.empty:
        raise ValueError("returns must not be empty")
    if returns.iloc[1:].isna().any():
        raise ValueError("returns contain missing observations after the first value")
    clean_returns = returns.copy()
    if pd.isna(clean_returns.iloc[0]):
        clean_returns.iloc[0] = 0.0
    return clean_returns