"""Structured model complexity versus predictive performance comparison.

Timing measurements are approximate, environment-dependent diagnostics and must
not be presented as universal benchmarks. The goal is to ask whether additional
complexity produces enough improvement to justify itself.
"""

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd
import torch

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
from ml.neural.dataset import FinancialSequenceDataset
from ml.neural.loaders import create_sequence_loader
from ml.neural.lstm import LSTMClassifier, LSTMRegressor
from ml.neural.sequences import create_sequences
from ml.preprocessing import TrainOnlyScaler
from ml.training.config import TrainingConfig
from ml.training.trainer import train_lstm


@dataclass(frozen=True)
class ComplexityComparisonRow:
    """One model family entry in a complexity-versus-performance table."""

    model_name: str
    parameter_count: int | None
    training_seconds: float
    inference_seconds: float
    metrics: dict[str, float]
    lookback_required: int | None
    preprocessing_required: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class ComplexityComparisonResult:
    """Full comparison across naive, linear, tree, boosting, and LSTM models."""

    task: str
    rows: tuple[ComplexityComparisonRow, ...]
    notes: tuple[str, ...]


def compare_model_complexity(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_validation: pd.DataFrame,
    y_validation: pd.Series,
    *,
    task: str = "regression",
    lookback: int = 5,
    hidden_size: int = 8,
    training_config: TrainingConfig | None = None,
) -> ComplexityComparisonResult:
    """Fit comparable models and record complexity, timing, and validation metrics."""
    if task not in {"regression", "classification"}:
        raise ValueError("task must be 'regression' or 'classification'")

    scaler = TrainOnlyScaler.create()
    X_train_scaled = scaler.fit_transform(X_train)
    X_validation_scaled = scaler.transform(X_validation)
    rows: list[ComplexityComparisonRow] = []

    for model in _baseline_models(task):
        rows.append(
            _evaluate_tabular_model(
                model,
                X_train_scaled,
                y_train,
                X_validation_scaled,
                y_validation,
                task=task,
                preprocessing_required=True,
            )
        )

    rows.append(
        _evaluate_lstm(
            X_train_scaled,
            y_train,
            X_validation_scaled,
            y_validation,
            task=task,
            lookback=lookback,
            hidden_size=hidden_size,
            training_config=training_config
            or TrainingConfig(epochs=1, patience=1, device="cpu", seed=42),
        )
    )

    return ComplexityComparisonResult(
        task=task,
        rows=tuple(rows),
        notes=(
            "training and inference timings are approximate local diagnostics",
            "do not treat timings as universal benchmark performance",
            "validation partition only; test holdout remains unused",
            "ask whether additional complexity justifies any metric improvement",
        ),
    )


def count_trainable_parameters(model: torch.nn.Module) -> int:
    """Count trainable PyTorch parameters for LSTM complexity reporting."""
    return int(sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad))


def _baseline_models(task: str) -> list[Any]:
    if task == "regression":
        return [
            NaiveRegression(),
            LinearRegressionModel(),
            RandomForestRegressionModel(n_estimators=20, random_state=42),
            GradientBoostingRegressionModel(),
        ]
    return [
        NaiveDirection(),
        LogisticDirectionModel(),
        RandomForestClassificationModel(n_estimators=20, random_state=42),
        GradientBoostingClassificationModel(),
    ]


def _evaluate_tabular_model(
    model,
    X_train,
    y_train,
    X_validation,
    y_validation,
    *,
    task: str,
    preprocessing_required: bool,
) -> ComplexityComparisonRow:
    start = perf_counter()
    model.fit(X_train, y_train)
    training_seconds = perf_counter() - start
    start = perf_counter()
    predicted = model.predict(X_validation)
    inference_seconds = perf_counter() - start
    probabilities = model.predict_proba(X_validation) if hasattr(model, "predict_proba") else None
    metrics = _metrics(task, y_validation, predicted, probabilities)
    parameter_count = _sklearn_parameter_count(model)
    return ComplexityComparisonRow(
        model_name=model.name,
        parameter_count=parameter_count,
        training_seconds=float(training_seconds),
        inference_seconds=float(inference_seconds),
        metrics=metrics,
        lookback_required=None,
        preprocessing_required=preprocessing_required,
        notes=("tabular model; no sequence lookback",),
    )


def _evaluate_lstm(
    X_train,
    y_train,
    X_validation,
    y_validation,
    *,
    task: str,
    lookback: int,
    hidden_size: int,
    training_config: TrainingConfig,
) -> ComplexityComparisonRow:
    train_x, train_y = create_sequences(X_train.to_numpy(), y_train.to_numpy(), lookback)
    val_x, val_y = create_sequences(X_validation.to_numpy(), y_validation.to_numpy(), lookback)
    train_loader = create_sequence_loader(FinancialSequenceDataset(train_x, train_y), 32)
    validation_loader = create_sequence_loader(FinancialSequenceDataset(val_x, val_y), 32)
    model_type = LSTMRegressor if task == "regression" else LSTMClassifier
    model = model_type(input_size=X_train.shape[1], hidden_size=hidden_size)
    parameter_count = count_trainable_parameters(model)
    start = perf_counter()
    result = train_lstm(
        model,
        train_loader,
        validation_loader,
        task=task,
        configuration=training_config,
    )
    training_seconds = perf_counter() - start
    start = perf_counter()
    from ml.training.epochs import validate_epoch
    from ml.training.optimization import create_loss

    _, predictions, _ = validate_epoch(
        result.model,
        validation_loader,
        create_loss(task),
        result.configuration.torch_device(),
    )
    inference_seconds = perf_counter() - start
    predicted = predictions.detach().cpu().numpy()
    if task == "classification":
        probabilities = 1 / (1 + np.exp(-predicted))
        class_pred = (probabilities >= 0.5).astype(int)
        metrics = _metrics(task, val_y, class_pred, probabilities)
    else:
        metrics = _metrics(task, val_y, predicted, None)
    return ComplexityComparisonRow(
        model_name="lstm",
        parameter_count=parameter_count,
        training_seconds=float(training_seconds),
        inference_seconds=float(inference_seconds),
        metrics=metrics,
        lookback_required=lookback,
        preprocessing_required=True,
        notes=(
            "trainable parameter count from PyTorch",
            "requires sequence lookback windows",
            "timing is approximate and environment-dependent",
        ),
    )


def _metrics(task, y_true, predicted, probabilities) -> dict[str, float]:
    if task == "regression":
        metrics = evaluate_regression(y_true, predicted)
    else:
        metrics = evaluate_classification(y_true, predicted, probabilities)
    return {
        key: float(value)
        for key, value in metrics.items()
        if isinstance(value, (int, float, np.floating)) and not isinstance(value, bool)
    }


def _sklearn_parameter_count(model) -> int | None:
    if not hasattr(model, "model"):
        return 0
    estimator = model.model
    if hasattr(estimator, "coef_"):
        count = int(np.asarray(estimator.coef_).size)
        if hasattr(estimator, "intercept_"):
            count += int(np.asarray(estimator.intercept_).size)
        return count
    if hasattr(estimator, "n_features_in_"):
        # Tree ensembles do not have a single dense parameter vector.
        return None
    return None
