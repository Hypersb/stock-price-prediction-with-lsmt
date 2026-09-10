"""Persisted experiment HTTP routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError
from backend.app.db.session import get_db_session
from backend.app.repositories.experiments import ExperimentRepository
from backend.app.schemas.persistence import (
    ExperimentDetail,
    ExperimentListResponse,
    ExperimentMetricResponse,
    ExperimentMetricsResponse,
    ExperimentSummary,
)

router = APIRouter(prefix="/experiments", tags=["experiments"])

MAX_LIMIT = 100


@router.get("", response_model=ExperimentListResponse)
def list_experiments(
    session: Annotated[Session, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    symbol: Annotated[str | None, Query()] = None,
) -> ExperimentListResponse:
    """List stored research experiments with pagination."""
    repo = ExperimentRepository(session)
    items, total = repo.list(limit=limit, offset=offset, symbol=symbol)
    return ExperimentListResponse(
        items=[ExperimentSummary.model_validate(item, from_attributes=True) for item in items],
        total=total,
        limit=limit,
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
