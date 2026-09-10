"""Validation-only comparison of baseline models."""

from dataclasses import dataclass

from ml.evaluation.classification import evaluate_classification
from ml.evaluation.regression import evaluate_regression
from ml.models.baselines import NaiveDirection, NaiveRegression
from ml.models.boosting import (
    GradientBoostingClassificationModel,
    GradientBoostingRegressionModel,
)
from ml.models.classification import LogisticDirectionModel
from ml.models.ensemble import (
    RandomForestClassificationModel,
    RandomForestRegressionModel,
)
from ml.models.regression import LinearRegressionModel
from ml.supervised import SupervisedDataset


@dataclass(frozen=True)
class ModelComparisonResult:
    """Metrics and metadata for one validation-set model comparison result."""

    model_name: str
    task_type: str
    dataset_split: str
    metrics: dict[str, object]
    training_configuration: dict[str, object]


def compare_regression_models(dataset: SupervisedDataset) -> list[ModelComparisonResult]:
    """Fit regression baselines on train and compare them on validation only."""
    models = [
        NaiveRegression(),
        LinearRegressionModel(),
        RandomForestRegressionModel(),
        GradientBoostingRegressionModel(),
    ]
    results = []
    for model in models:
        model.fit(dataset.X_train, dataset.y_train)
        metrics = evaluate_regression(
            dataset.y_validation,
            model.predict(dataset.X_validation),
        )
        results.append(_result(model, "regression", metrics))
    return results


def compare_classification_models(dataset: SupervisedDataset) -> list[ModelComparisonResult]:
    """Fit classification baselines on train and compare them on validation only."""
    models = [
        NaiveDirection(),
        LogisticDirectionModel(),
        RandomForestClassificationModel(),
        GradientBoostingClassificationModel(),
    ]
    results = []
    for model in models:
        model.fit(dataset.X_train, dataset.y_train)
        predictions = model.predict(dataset.X_validation)
        probabilities = model.predict_proba(dataset.X_validation) if hasattr(model, "predict_proba") else None
        metrics = evaluate_classification(dataset.y_validation, predictions, probabilities)
        results.append(_result(model, "classification", metrics))
    return results


def _result(model, task_type: str, metrics: dict[str, object]) -> ModelComparisonResult:
    configuration = {
        key: value
        for key, value in model.model.get_params().items()
    } if hasattr(model, "model") else {}
    return ModelComparisonResult(
        model_name=model.name,
        task_type=task_type,
        dataset_split="validation",
        metrics=metrics,
        training_configuration=configuration,
    )