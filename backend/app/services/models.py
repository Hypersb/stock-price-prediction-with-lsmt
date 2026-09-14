"""Model catalog and prediction lookup services."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.errors import NotFoundError
from backend.app.repositories.walk_forward import PredictionRepository
from backend.app.schemas.common import TaskType
from backend.app.schemas.models import (
    ModelCatalogResponse,
    PredictionPoint,
    PredictionResponse,
    SupportedModel,
)
from ml.registry.store import ModelRegistryStore

SUPPORTED_MODELS: tuple[SupportedModel, ...] = (
    SupportedModel(
        name="naive",
        family="baseline",
        tasks=[TaskType.REGRESSION, TaskType.CLASSIFICATION],
        trained=False,
        description="Naive persistence baseline for research comparisons.",
    ),
    SupportedModel(
        name="linear_regression",
        family="baseline",
        tasks=[TaskType.REGRESSION],
        trained=False,
        description="Ordinary least squares regression baseline.",
    ),
    SupportedModel(
        name="logistic_regression",
        family="baseline",
        tasks=[TaskType.CLASSIFICATION],
        trained=False,
        description="Logistic regression direction classifier.",
    ),
    SupportedModel(
        name="random_forest",
        family="baseline",
        tasks=[TaskType.REGRESSION, TaskType.CLASSIFICATION],
        trained=False,
        description="Random forest baseline for tabular features.",
    ),
    SupportedModel(
        name="gradient_boosting",
        family="baseline",
        tasks=[TaskType.REGRESSION, TaskType.CLASSIFICATION],
        trained=False,
        description="Gradient boosting baseline for tabular features.",
    ),
    SupportedModel(
        name="lstm",
        family="neural",
        tasks=[TaskType.REGRESSION, TaskType.CLASSIFICATION],
        trained=False,
        description="Sequence LSTM architecture; training is not triggered by GET.",
    ),
)


class ModelService:
    """Expose model metadata and persisted OOS prediction lookups without training."""

    def __init__(
        self,
        session: Session | None = None,
        *,
        registry: ModelRegistryStore | None = None,
        registry_path: Path | str | None = None,
    ) -> None:
        self.session = session
        self._registry = registry
        self._registry_path = registry_path

    def _registry_store(self) -> ModelRegistryStore:
        if self._registry is not None:
            return self._registry
        return ModelRegistryStore(self._registry_path)

    def list_models(self) -> ModelCatalogResponse:
        # Algorithm catalog stays fixed; trained=True only when a registry
        # record points at an existing artifact file. Empty registry → all False.
        trained_algorithms = self._registry_store().algorithms_with_artifacts()
        models = [
            item.model_copy(
                update={"trained": item.name.lower() in trained_algorithms}
            )
            for item in SUPPORTED_MODELS
        ]
        return ModelCatalogResponse(models=models, count=len(models))

    def get_predictions(
        self,
        symbol: str,
        model: str,
        task: TaskType,
        *,
        experiment_id: UUID | None = None,
        walk_forward_run_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> PredictionResponse:
        known = {item.name for item in SUPPORTED_MODELS}
        if model.lower() not in known:
            raise NotFoundError(f"unsupported model family: {model}")

        symbol_key = symbol.strip().upper()
        model_key = model.lower()
        if self.session is None:
            return PredictionResponse(
                symbol=symbol_key,
                model=model_key,
                task=task,
                available=False,
                message=(
                    "database persistence is not configured; "
                    "this endpoint does not train models and returns only stored oos predictions"
                ),
                predictions=[],
            )

        rows = PredictionRepository(self.session).list_filtered(
            symbol=symbol_key,
            model_name=model_key,
            task=task.value,
            experiment_id=experiment_id,
            walk_forward_run_id=walk_forward_run_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        if not rows:
            return PredictionResponse(
                symbol=symbol_key,
                model=model_key,
                task=task,
                available=False,
                message=(
                    "no persisted out-of-sample predictions matched the query; "
                    "this endpoint does not train models"
                ),
                predictions=[],
            )
        points = [
            PredictionPoint(
                prediction_date=row.prediction_date,
                forecast_horizon=None,
                predicted_return=row.predicted_value,
                direction_probability=row.predicted_probability,
                predicted_direction=row.predicted_class,
            )
            for row in rows
        ]
        return PredictionResponse(
            symbol=symbol_key,
            model=model_key,
            task=task,
            available=True,
            message="persisted out-of-sample research predictions",
            predictions=points,
        )
