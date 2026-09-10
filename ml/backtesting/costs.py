"""Turnover and simplified research execution costs."""

import pandas as pd


def calculate_turnover(position: pd.Series) -> pd.Series:
    """Calculate absolute position changes, with initial turnover from flat."""
    if not isinstance(position, pd.Series):
        raise TypeError("position must be a pandas Series")
    previous = position.shift(1).fillna(0.0)
    return (position - previous).abs().rename("turnover")


def calculate_costs(
    turnover: pd.Series,
    transaction_cost_bps: float,
    slippage_bps: float,
) -> pd.Series:
    """Apply turnover times transaction-cost plus slippage rates."""
    if transaction_cost_bps < 0 or slippage_bps < 0:
        raise ValueError("costs must be nonnegative")
    rate = (transaction_cost_bps + slippage_bps) / 10000
    return (turnover * rate).rename("trading_cost")