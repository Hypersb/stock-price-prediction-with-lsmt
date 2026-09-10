"""Model metadata and prediction response schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from backend.app.schemas.common import TaskType


class SupportedModel(BaseModel):
    """Description of a research model family exposed by the API."""

    name: str
    family: str
    tasks: list[TaskType]
    trained: bool = False
    description: str


class ModelCatalogResponse(BaseModel):
    """Catalog of supported research models without training claims."""

    models: list[SupportedModel]
    count: int = Field(ge=0)


class PredictionPoint(BaseModel):
    """Single stored research prediction observation."""

    prediction_date: date
    forecast_horizon: int | None = None
    predicted_return: float | None = None
    direction_probability: float | None = None
    predicted_direction: int | None = None


class PredictionResponse(BaseModel):
    """Prediction payload backed by stored research artifacts when available."""

    symbol: str
    model: str
    task: TaskType
    available: bool
    message: str
    predictions: list[PredictionPoint] = Field(default_factory=list)
