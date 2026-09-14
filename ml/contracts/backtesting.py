"""Backtesting boundary helpers."""

from __future__ import annotations

from typing import Final

from ml.errors import BacktestError

SUPPORTED_BACKTEST_HORIZON: Final[int] = 1


def assert_supported_backtest_horizon(forecast_horizon: int) -> None:
    """Fail loudly unless strategy backtests use the supported horizon."""
    if forecast_horizon != SUPPORTED_BACKTEST_HORIZON:
        raise BacktestError(
            "execution alignment currently supports forecast_horizon="
            f"{SUPPORTED_BACKTEST_HORIZON} only; multi-period strategy "
            "backtesting is not implemented"
        )
