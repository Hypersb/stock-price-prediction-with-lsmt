"""Walk-forward evaluation of non-neural baseline models."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

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
from ml.validation.config import WalkForwardConfig
from ml.validation.folds import WalkForwardFold
from ml.validation.preprocessing import preprocess_fold
from ml.validation.purging import purge_fold


@dataclass(frozen=True)
class WalkForwardModelResult:
    """One model's metrics and out-of-sample predictions for one fold."""

    fold: int
    model_name: str
    task: str
    metrics: dict[str, object]
    dates: pd.DatetimeIndex
    actual: np.ndarray
    predicted: np.ndarray
    probabilities: np.ndarray | None = None


def evaluate_baselines_walk_forward(
    X: pd.DataFrame,
    y: pd.Series,
    dates: pd.Series | pd.Index,
    folds: list[WalkForwardFold],
    *,
    task: str,
    config: WalkForwardConfig,
) -> list[WalkForwardModelResult]:
    """Fit fresh baseline models per purged fold and evaluate each test window."""
    if task not in {"regression", "classification"}:
        raise ValueError("task must be 'regression' or 'classification'")
    parsed_dates = pd.DatetimeIndex(pd.to_datetime(dates))
    results: list[WalkForwardModelResult] = []
    for fold in folds:
        safe_fold = purge_fold(fold, config)
        transformed = preprocess_fold(
            X.iloc[safe_fold.train_indices],
            X.iloc[safe_fold.validation_indices],
            X.iloc[safe_fold.test_indices],
        )
        if task == "regression":
            models = [
                NaiveRegression(),
                LinearRegressionModel(),
                RandomForestRegressionModel(n_estimators=20),
                GradientBoostingRegressionModel(),
            ]
        else:
            models = [
                NaiveDirection(),
                LogisticDirectionModel(),
                RandomForestClassificationModel(n_estimators=20),
                GradientBoostingClassificationModel(),
            ]
        for model in models:
            model.fit(
                transformed.X_train,
                y.iloc[safe_fold.train_indices],
            )
            actual = y.iloc[safe_fold.test_indices].to_numpy()
            predicted = model.predict(transformed.X_test)
            probabilities = model.predict_proba(transformed.X_test)[:, 1] if hasattr(model, "predict_proba") else None
            metrics = (
                evaluate_regression(actual, predicted)
                if task == "regression"
                else evaluate_classification(actual, predicted, probabilities)
            )
            results.append(
                WalkForwardModelResult(
                    safe_fold.fold,
                    model.name,
                    task,
                    metrics,
                    parsed_dates[safe_fold.test_indices],
                    actual,
                    predicted,
                    probabilities,
                )
            )
    return results