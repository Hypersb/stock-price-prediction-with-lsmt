"""Simple portfolio analytics without brokerage connectivity."""

from __future__ import annotations

import math

from ml.portfolio.positions import Portfolio


def position_weights(portfolio: Portfolio) -> dict[str, float]:
    """Return market-value weights keyed by symbol (sum to 1 when value > 0)."""
    total = portfolio.total_value
    if total <= 0:
        return {p.symbol: 0.0 for p in portfolio.positions}
    return {p.symbol: p.market_value / total for p in portfolio.positions}


def portfolio_return(portfolio: Portfolio) -> float:
    """Weighted sum of per-position returns; requires each ``return_`` set."""
    weights = position_weights(portfolio)
    if not portfolio.positions:
        raise ValueError("portfolio has no positions")
    total = 0.0
    for position in portfolio.positions:
        if position.return_ is None:
            raise ValueError(
                f"position {position.symbol} missing return_; "
                "refusing to fabricate returns"
            )
        total += weights[position.symbol] * float(position.return_)
    return float(total)


def concentration_hhi(portfolio: Portfolio) -> float:
    """Herfindahl–Hirschman Index of position weights (0–1 scale for weights)."""
    weights = position_weights(portfolio)
    if not weights:
        return 0.0
    return float(sum(w * w for w in weights.values()))


def portfolio_volatility(
    portfolio: Portfolio,
    *,
    position_volatilities: dict[str, float] | None = None,
    returns: list[float] | None = None,
) -> float:
    """Simple volatility estimate from weighted returns or weighted vols.

    Prefer ``returns`` (portfolio period returns) when provided: returns sample
    stdev. Otherwise, if ``position_volatilities`` is provided, use a diagonal
    (zero-correlation) weighted sum of variances. Missing inputs raise rather
    than inventing correlations or vols.
    """
    if returns is not None:
        if len(returns) < 2:
            raise ValueError("need at least two portfolio returns for volatility")
        mean = sum(returns) / len(returns)
        var = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        return float(math.sqrt(var))

    if position_volatilities is None:
        raise ValueError(
            "provide returns or position_volatilities; refusing fabricated volatility"
        )
    weights = position_weights(portfolio)
    variance = 0.0
    for position in portfolio.positions:
        if position.symbol not in position_volatilities:
            raise ValueError(f"missing volatility for {position.symbol}")
        vol = float(position_volatilities[position.symbol])
        if vol < 0:
            raise ValueError("volatilities must be non-negative")
        w = weights[position.symbol]
        variance += (w * vol) ** 2
    return float(math.sqrt(variance))