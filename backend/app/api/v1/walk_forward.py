"""Persisted walk-forward HTTP routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError
from backend.app.db.session import get_db_session
from backend.app.repositories.walk_forward import WalkForwardRepository
from backend.app.schemas.persistence import (
    WalkForwardFoldResponse,
    WalkForwardRunResponse,
)

router = APIRouter(prefix="/walk-forward", tags=["walk-forward"])


@router.get("/{run_id}", response_model=WalkForwardRunResponse)
def get_walk_forward_run(
    run_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
) -> WalkForwardRunResponse:
    """Return one stored walk-forward run with folds."""
    run = WalkForwardRepository(session).get_run(run_id)
    if run is None:
        raise NotFoundError(f"walk-forward run not found: {run_id}")
    return WalkForwardRunResponse(
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
