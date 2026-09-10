"""Exposure, turnover, and simple contiguous-trade diagnostics."""

import pandas as pd


def strategy_analytics(positions: pd.Series, net_returns: pd.Series) -> dict[str, float | int]:
    """Summarize exposure, turnover, position changes, and completed segments."""
    if len(positions) != len(net_returns):
        raise ValueError("positions and returns must have matching lengths")
    position = pd.Series(positions).reset_index(drop=True)
    returns = pd.Series(net_returns).reset_index(drop=True)
    turnover = position.diff().abs().fillna(position.abs())
    changes = int((turnover > 0).sum())
    segments: list[float] = []
    current_position = 0.0
    current_returns: list[float] = []
    for value, position_value in zip(returns, position):
        if position_value != current_position:
            if current_position != 0 and current_returns:
                segments.append(float((1 + pd.Series(current_returns)).prod() - 1))
            current_returns = []
            current_position = position_value
        if current_position != 0:
            current_returns.append(value)
    if current_position != 0 and current_returns:
        segments.append(float((1 + pd.Series(current_returns)).prod() - 1))
    winning = sum(value > 0 for value in segments)
    return {
        "long_exposure": float((position > 0).mean()),
        "short_exposure": float((position < 0).mean()),
        "flat_exposure": float((position == 0).mean()),
        "average_absolute_exposure": float(position.abs().mean()),
        "total_turnover": float(turnover.sum()),
        "average_turnover": float(turnover.mean()),
        "position_changes": changes,
        "completed_trades": len(segments),
        "winning_trades": winning,
        "losing_trades": len(segments) - winning,
        "trade_win_rate": float(winning / len(segments)) if segments else 0.0,
        "average_trade_return": float(pd.Series(segments).mean()) if segments else 0.0,
    }