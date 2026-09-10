"""Backtesting HTTP routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_backtest_service
from backend.app.schemas.backtests import BacktestRequest, BacktestResponse
from backend.app.services.backtests import BacktestService

router = APIRouter(prefix="/backtests", tags=["backtests"])


@router.post("", response_model=BacktestResponse)
def create_backtest(
    request: BacktestRequest,
    service: Annotated[BacktestService, Depends(get_backtest_service)],
) -> BacktestResponse:
    """Run a research backtest from explicit out-of-sample prediction inputs."""
    return service.run(request)
