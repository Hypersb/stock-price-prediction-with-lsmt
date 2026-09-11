"""Model metadata and prediction HTTP routes."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.db.session import get_database
from backend.app.dependencies import get_model_service
from backend.app.schemas.common import TaskType
from backend.app.schemas.models import ModelCatalogResponse, PredictionResponse
from backend.app.services.models import ModelService

router = APIRouter(prefix="/models", tags=["models"])


def _optional_db_session():
    """Yield a DB session when persistence is configured; otherwise None."""
    try:
        database = get_database()
    except RuntimeError:
        yield None
        return
    session = database.create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@router.get("", response_model=ModelCatalogResponse)
def list_models(
    service: Annotated[ModelService, Depends(get_model_service)],
) -> ModelCatalogResponse:
    """List supported research model families without claiming trained artifacts."""
    return service.list_models()


@router.get("/{model}/predictions/{symbol}", response_model=PredictionResponse)
def get_model_predictions(
    model: str,
    symbol: str,
    task: Annotated[TaskType, Query(description="regression or classification")],
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session | None, Depends(_optional_db_session)],
    experiment_id: Annotated[UUID | None, Query()] = None,
    walk_forward_run_id: Annotated[UUID | None, Query()] = None,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    limit: Annotated[int, Query(ge=1)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PredictionResponse:
    """Return persisted OOS predictions only; never trains models on GET."""
    service = ModelService(session=session)
    return service.get_predictions(
        symbol,
        model,
        task,
        experiment_id=experiment_id,
        walk_forward_run_id=walk_forward_run_id,
        start_date=start_date,
        end_date=end_date,
        limit=min(limit, settings.max_page_size),
        offset=offset,
    )
