"""Persisted experiment HTTP routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import NotFoundError
from backend.app.db.session import get_db_session
from backend.app.repositories.backtests import BacktestRepository
from backend.app.repositories.experiments import ExperimentRepository
from backend.app.repositories.walk_forward import WalkForwardRepository
from backend.app.schemas.persistence import (
    ExperimentDetail,
    ExperimentListResponse,
    ExperimentMetricResponse,
    ExperimentMetricsResponse,
    ExperimentRelatedResponse,
    ExperimentSummary,
    PersistedBacktestSummary,
    WalkForwardFoldResponse,
    WalkForwardRunResponse,
)

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("", response_model=ExperimentListResponse)
def list_experiments(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    limit: Annotated[int, Query(ge=1)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    symbol: Annotated[str | None, Query()] = None,
) -> ExperimentListResponse:
    """List stored research experiments with pagination."""
    capped = min(limit, settings.max_page_size)
    repo = ExperimentRepository(session)
    items, total = repo.list(limit=capped, offset=offset, symbol=symbol)
    return ExperimentListResponse(
        items=[ExperimentSummary.model_validate(item, from_attributes=True) for item in items],
        total=total,
        limit=capped,
        offset=offset,
    )


@router.get("/{experiment_id}", response_model=ExperimentDetail)
def get_experiment(
    experiment_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
) -> ExperimentDetail:
    """Return one stored experiment."""
    experiment = ExperimentRepository(session).get(experiment_id)
    if experiment is None:
        raise NotFoundError(f"experiment not found: {experiment_id}")
    return ExperimentDetail.model_validate(experiment, from_attributes=True)


@router.get("/{experiment_id}/metrics", response_model=ExperimentMetricsResponse)
def get_experiment_metrics(
    experiment_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
) -> ExperimentMetricsResponse:
    """Return metrics for one stored experiment."""
    repo = ExperimentRepository(session)
    if repo.get(experiment_id) is None:
        raise NotFoundError(f"experiment not found: {experiment_id}")
    metrics = repo.list_metrics(experiment_id)
    return ExperimentMetricsResponse(
        experiment_id=experiment_id,
        metrics=[
            ExperimentMetricResponse.model_validate(item, from_attributes=True)
            for item in metrics
        ],
    )


@router.get("/{experiment_id}/related", response_model=ExperimentRelatedResponse)
def get_experiment_related(
    experiment_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ExperimentRelatedResponse:
    """Return linked walk-forward runs and backtests for one experiment.

    Does not execute research. Returns empty collections when no artifacts exist.
    """
    if ExperimentRepository(session).get(experiment_id) is None:
        raise NotFoundError(f"experiment not found: {experiment_id}")
    runs = WalkForwardRepository(session).list_by_experiment(
        experiment_id, limit=settings.max_page_size, offset=0
    )
    backtests, _ = BacktestRepository(session).list(
        limit=settings.max_page_size, offset=0, experiment_id=experiment_id
    )
    return ExperimentRelatedResponse(
        experiment_id=experiment_id,
        walk_forward_runs=[
            WalkForwardRunResponse(
                id=run.id,
                created_at=run.created_at,
                experiment_id=run.experiment_id,
                symbol=run.symbol,
                model_name=run.model_name,
                task=run.task,
                window_type=run.window_type,
                initial_train_size=run.initial_train_size,
                validation_size=run.validation_size,
                test_size=run.test_size,
                step_size=run.step_size,
                gap=run.gap,
                forecast_horizon=run.forecast_horizon,
                folds=[
                    WalkForwardFoldResponse.model_validate(fold, from_attributes=True)
                    for fold in run.folds
                ],
            )
            for run in runs
        ],
        backtests=[
            PersistedBacktestSummary.model_validate(item, from_attributes=True)
            for item in backtests
        ],
    )
