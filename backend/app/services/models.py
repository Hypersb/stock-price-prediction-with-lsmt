"""Model catalog and prediction lookup services."""

from __future__ import annotations

from backend.app.core.errors import NotFoundError
from backend.app.schemas.common import TaskType
from backend.app.schemas.models import (
    ModelCatalogResponse,
    PredictionPoint,
    PredictionResponse,
    SupportedModel,
)

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


class PredictionStore:
    """In-memory placeholder for future persisted experiment predictions."""

    def __init__(self) -> None:
        self._predictions: dict[tuple[str, str, str], list[PredictionPoint]] = {}

    def list_predictions(
        self, symbol: str, model: str, task: str
    ) -> list[PredictionPoint]:
        key = (symbol.upper(), model.lower(), task.lower())
        return list(self._predictions.get(key, []))

    def store_predictions(
        self,
        symbol: str,
        model: str,
        task: str,
        predictions: list[PredictionPoint],
    ) -> None:
        key = (symbol.upper(), model.lower(), task.lower())
        self._predictions[key] = list(predictions)


_DEFAULT_STORE = PredictionStore()


class ModelService:
    """Expose model metadata and stored prediction lookups without training."""

    def __init__(self, store: PredictionStore | None = None) -> None:
        self.store = store or _DEFAULT_STORE

    def list_models(self) -> ModelCatalogResponse:
        models = list(SUPPORTED_MODELS)
        return ModelCatalogResponse(models=models, count=len(models))

    def get_predictions(
        self,
        symbol: str,
        model: str,
        task: TaskType,
    ) -> PredictionResponse:
        known = {item.name for item in SUPPORTED_MODELS}
        if model.lower() not in known:
            raise NotFoundError(f"unsupported model family: {model}")

        stored = self.store.list_predictions(symbol, model, task.value)
        if not stored:
            return PredictionResponse(
                symbol=symbol.strip().upper(),
                model=model.lower(),
                task=task,
                available=False,
                message=(
                    "no stored prediction artifact is available; "
                    "this endpoint does not train models"
                ),
                predictions=[],
            )
        return PredictionResponse(
            symbol=symbol.strip().upper(),
            model=model.lower(),
            task=task,
            available=True,
            message="stored research predictions",
            predictions=stored,
        )
