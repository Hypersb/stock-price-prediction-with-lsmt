"""Backtesting HTTP routes for synchronous runs and persisted results."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError
from backend.app.db.session import get_db_session
from backend.app.dependencies import get_backtest_service
from backend.app.repositories.backtests import BacktestRepository
from backend.app.schemas.backtests import BacktestRequest, BacktestResponse
from backend.app.schemas.persistence import (
    PersistedBacktestDetail,
    PersistedBacktestListResponse,
    PersistedBacktestMetric,
    PersistedBacktestSummary,
    PersistedEquityPoint,
)
from backend.app.services.backtests import BacktestService

router = APIRouter(prefix="/backtests", tags=["backtests"])

MAX_LIMIT = 100


@router.post("", response_model=BacktestResponse)
def create_backtest(
    request: BacktestRequest,
    service: Annotated[BacktestService, Depends(get_backtest_service)],
) -> BacktestResponse:
    """Run a research backtest from explicit out-of-sample prediction inputs."""
    return service.run(request)


@router.get("", response_model=PersistedBacktestListResponse)
def list_persisted_backtests(
    session: Annotated[Session, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    symbol: Annotated[str | None, Query()] = None,
) -> PersistedBacktestListResponse:
    """List stored research backtests with pagination."""
    items, total = BacktestRepository(session).list(
        limit=limit, offset=offset, symbol=symbol
    )
    return PersistedBacktestListResponse(
        items=[
            PersistedBacktestSummary.model_validate(item, from_attributes=True)
            for item in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{backtest_id}", response_model=PersistedBacktestDetail)
def get_persisted_backtest(
    backtest_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
) -> PersistedBacktestDetail:
    """Return one stored backtest with metrics and equity curve."""
    run = BacktestRepository(session).get(backtest_id)
    if run is None:
        raise NotFoundError(f"backtest not found: {backtest_id}")
    return PersistedBacktestDetail(
        id=run.id,
        created_at=run.created_at,
        symbol=run.symbol,
        model_name=run.model_name,
        task=run.task,
        strategy_mode=run.strategy_mode,
        sample_kind=run.sample_kind,
        observation_count=run.observation_count,
        start_date=run.start_date,
        end_date=run.end_date,
        experiment_id=run.experiment_id,
        walk_forward_run_id=run.walk_forward_run_id,
        signal_threshold=run.signal_threshold,
        transaction_cost_bps=run.transaction_cost_bps,
        slippage_bps=run.slippage_bps,
        initial_capital=run.initial_capital,
        metrics=[
            PersistedBacktestMetric(
                metric_name=metric.metric_name,
                metric_value=metric.metric_value,
            )
            for metric in run.metrics
        ],
        equity_curve=[
            PersistedEquityPoint.model_validate(point, from_attributes=True)
            for point in run.equity_points
        ],
    )
