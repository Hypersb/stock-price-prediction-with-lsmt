"""Performance and risk metrics for historical strategy returns."""

import math

import numpy as np
import pandas as pd


def calculate_metrics(
    net_returns: pd.Series,
    *,
    annualization_factor: float = 252,
    risk_free_rate: float = 0.0,
) -> dict[str, float]:
    """Calculate compounded return, risk, and hit-rate metrics.

    Risk-free rate is an annual rate and is converted to a daily equivalent.
    Sharpe is annualized mean excess return divided by annualized volatility.
    """
    returns = pd.Series(net_returns).dropna().astype(float)
    if returns.empty or annualization_factor <= 0:
        raise ValueError("returns must be non-empty and annualization_factor positive")
    if (1 + returns <= 0).any():
        raise ValueError("returns must be greater than -100 percent")
    equity = (1 + returns).cumprod()
    total_return = float(equity.iloc[-1] - 1)
    annualized_return = float(equity.iloc[-1] ** (annualization_factor / len(returns)) - 1)
    annualized_volatility = float(returns.std(ddof=1) * math.sqrt(annualization_factor)) if len(returns) > 1 else 0.0
    daily_risk_free = (1 + risk_free_rate) ** (1 / annualization_factor) - 1
    excess = returns - daily_risk_free
    sharpe = float(excess.mean() * math.sqrt(annualization_factor) / annualized_volatility) if annualized_volatility else 0.0
    downside = excess.clip(upper=0)
    downside_deviation = float(np.sqrt((downside**2).mean()) * math.sqrt(annualization_factor))
    sortino = float(excess.mean() * math.sqrt(annualization_factor) / downside_deviation) if downside_deviation else 0.0
    drawdown = equity / equity.cummax() - 1
    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "maximum_drawdown": float(drawdown.min()),
        "hit_rate": float((returns > 0).mean()),
    }