"""Strategy return and equity-curve calculations."""

import pandas as pd

from ml.backtesting.costs import calculate_costs, calculate_turnover


def calculate_strategy_returns(
    positions: pd.Series,
    realized_returns: pd.Series,
    *,
    transaction_cost_bps: float = 0.0,
    slippage_bps: float = 0.0,
    initial_capital: float = 1.0,
) -> pd.DataFrame:
    """Calculate gross/net returns and compounded equity without dropping rows."""
    if len(positions) != len(realized_returns):
        raise ValueError("positions and realized returns must have matching lengths")
    if initial_capital <= 0:
        raise ValueError("initial_capital must be positive")
    turnover = calculate_turnover(positions.reset_index(drop=True))
    gross = positions.reset_index(drop=True) * realized_returns.reset_index(drop=True)
    costs = calculate_costs(turnover, transaction_cost_bps, slippage_bps)
    net = gross - costs
    if (1 + net <= 0).any():
        raise ValueError("net returns must be greater than -100 percent")
    equity = initial_capital * (1 + net).cumprod()
    return pd.DataFrame(
        {
            "position": positions.to_numpy(),
            "realized_return": realized_returns.to_numpy(),
            "turnover": turnover,
            "trading_cost": costs,
            "gross_strategy_return": gross,
            "net_strategy_return": net,
            "equity": equity,
        },
        index=positions.index,
    )