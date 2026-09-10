"""Model metadata and prediction HTTP routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.dependencies import get_model_service
from backend.app.schemas.common import TaskType
from backend.app.schemas.models import ModelCatalogResponse, PredictionResponse
from backend.app.services.models import ModelService

router = APIRouter(prefix="/models", tags=["models"])


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
    service: Annotated[ModelService, Depends(get_model_service)],
) -> PredictionResponse:
    """Return stored predictions only; never trains models on GET."""
    return service.get_predictions(symbol, model, task)
