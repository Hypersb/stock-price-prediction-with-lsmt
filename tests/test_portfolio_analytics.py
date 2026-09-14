"""Tests for local portfolio analytics (no brokerage)."""

from __future__ import annotations

import pytest

from ml.portfolio import (
    Portfolio,
    Position,
    concentration_hhi,
    portfolio_return,
    portfolio_volatility,
    position_weights,
)


def test_weights_and_return() -> None:
    portfolio = Portfolio(
        positions=(
            Position(symbol="AAPL", quantity=10, price=100.0, return_=0.10),
            Position(symbol="MSFT", quantity=5, price=200.0, return_=0.00),
        )
    )
    weights = position_weights(portfolio)
    assert weights["AAPL"] == pytest.approx(0.5)
    assert weights["MSFT"] == pytest.approx(0.5)
    assert portfolio_return(portfolio) == pytest.approx(0.05)


def test_concentration_hhi_equal_weights() -> None:
    portfolio = Portfolio(
        positions=(
            Position(symbol="AAA", quantity=1, price=50.0),
            Position(symbol="BBB", quantity=1, price=50.0),
        )
    )
    assert concentration_hhi(portfolio) == pytest.approx(0.5)


def test_volatility_from_returns_and_missing_inputs() -> None:
    portfolio = Portfolio(
        positions=(Position(symbol="AAA", quantity=1, price=100.0),)
    )
    vol = portfolio_volatility(portfolio, returns=[0.01, -0.02, 0.015, 0.0])
    assert vol >= 0
    with pytest.raises(ValueError, match="refusing fabricated"):
        portfolio_volatility(portfolio)


def test_portfolio_return_refuses_missing_position_returns() -> None:
    portfolio = Portfolio(
        positions=(Position(symbol="AAA", quantity=1, price=10.0),)
    )
    with pytest.raises(ValueError, match="missing return_"):
        portfolio_return(portfolio)
