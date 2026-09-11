"""Model explainability utilities with explicit methodological caveats.

Tree models expose native impurity-based importances where available.
Linear and logistic models expose coefficients; interpretation depends on
feature scaling because training uses train-only standardization.

For LSTM models this module does not invent causal feature importance.
Optional permutation-based sequence feature sensitivity measures predictive
degradation when one feature channel is shuffled across evaluation sequences.
That is a sensitivity measure, not causal attribution.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml.evaluation.classification import evaluate_classification
from ml.evaluation.regression import evaluate_regression


@dataclass(frozen=True)
class FeatureImportanceResult:
    """Structured explainability output for one model and method."""

    model_name: str
    method: str
    task: str
    importances: tuple[tuple[str, float], ...]
    notes: tuple[str, ...]


def tree_native_importance(model, feature_names: tuple[str, ...] | list[str]) -> FeatureImportanceResult:
    """Return impurity-based feature importance from a fitted tree ensemble."""
    if not hasattr(model, "model") or not hasattr(model.model, "feature_importances_"):
        raise ValueError("model does not expose native feature_importances_")
    names = tuple(feature_names)
    values = np.asarray(model.model.feature_importances_, dtype=float)
    if len(names) != len(values):
        raise ValueError("feature_names length must match importance vector")
    ranked = tuple(
        sorted(
            ((name, float(value)) for name, value in zip(names, values, strict=True)),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    return FeatureImportanceResult(
        model_name=getattr(model, "name", model.__class__.__name__),
        method="tree_native_impurity",
        task="unknown",
        importances=ranked,
        notes=(
            "native impurity-based importance from the fitted tree ensemble",
            "biased toward high-cardinality features; not causal attribution",
        ),
    )


def linear_coefficients(
    model,
    feature_names: tuple[str, ...] | list[str],
    *,
    scaled_features: bool = True,
) -> FeatureImportanceResult:
    """Return linear/logistic coefficients paired with feature names."""
    if not hasattr(model, "model") or not hasattr(model.model, "coef_"):
        raise ValueError("model does not expose coefficients")
    names = tuple(feature_names)
    coef = np.asarray(model.model.coef_, dtype=float).reshape(-1)
    if len(names) != len(coef):
        raise ValueError("feature_names length must match coefficient vector")
    ranked = tuple(
        sorted(
            ((name, float(value)) for name, value in zip(names, coef, strict=True)),
            key=lambda item: abs(item[1]),
            reverse=True,
        )
    )
    notes = [
        "coefficients are linear associations conditional on other features",
        "not causal feature importance",
    ]
    if scaled_features:
        notes.append(
            "features were scaled with train-only standardization; "
            "coefficient magnitude is in standardized units and is not "
            "directly comparable to raw-price or raw-return units"
        )
    else:
        notes.append("features were not reported as scaled; interpret units carefully")
    intercept = getattr(model.model, "intercept_", None)
    if intercept is not None:
        notes.append(f"intercept={float(np.asarray(intercept).reshape(-1)[0])}")
    return FeatureImportanceResult(
        model_name=getattr(model, "name", model.__class__.__name__),
        method="linear_coefficients",
        task="unknown",
        importances=ranked,
        notes=tuple(notes),
    )


def permutation_importance(
    predict_fn: Callable[[pd.DataFrame], np.ndarray],
    X: pd.DataFrame,
    y: pd.Series | np.ndarray,
    *,
    model_name: str,
    task: str,
    metric: str = "rmse",
    n_repeats: int = 5,
    random_state: int = 42,
    probabilities_fn: Callable[[pd.DataFrame], np.ndarray] | None = None,
) -> FeatureImportanceResult:
    """Compute permutation importance on a fixed evaluation partition.

    The caller must supply validation- or test-safe matrices that were not used
    for fitting the evaluated model. Higher positive values mean larger metric
    degradation after permuting the feature (worse predictive performance).
    """
    if task not in {"regression", "classification"}:
        raise ValueError("task must be 'regression' or 'classification'")
    if n_repeats <= 0:
        raise ValueError("n_repeats must be positive")
    baseline = _score(predict_fn, X, y, task, metric, probabilities_fn)
    rng = np.random.default_rng(random_state)
    importances: list[tuple[str, float]] = []
    for column in X.columns:
        deltas: list[float] = []
        for _ in range(n_repeats):
            shuffled = X.copy()
            shuffled[column] = rng.permutation(shuffled[column].to_numpy())
            permuted = _score(predict_fn, shuffled, y, task, metric, probabilities_fn)
            deltas.append(_degradation(baseline, permuted, metric))
        importances.append((column, float(np.mean(deltas))))
    ranked = tuple(sorted(importances, key=lambda item: item[1], reverse=True))
    return FeatureImportanceResult(
        model_name=model_name,
        method="permutation_importance",
        task=task,
        importances=ranked,
        notes=(
            f"baseline_{metric}={baseline}",
            "importance is mean metric degradation after feature permutation",
            "evaluation partition must not be used for fitting",
            "not causal attribution",
        ),
    )


def lstm_sequence_permutation_importance(
    sequences: np.ndarray,
    targets: np.ndarray,
    feature_names: tuple[str, ...] | list[str],
    predict_fn: Callable[[np.ndarray], np.ndarray],
    *,
    model_name: str = "lstm",
    task: str = "regression",
    metric: str = "rmse",
    n_repeats: int = 3,
    random_state: int = 42,
) -> FeatureImportanceResult:
    """Permutation-based sequence feature sensitivity for an LSTM.

    One feature channel is permuted across evaluation sequences while other
    channels remain unchanged. The resulting degradation is a sensitivity
    measure, not causal attribution, and must be labeled as such.
    """
    if sequences.ndim != 3:
        raise ValueError("sequences must have shape (batch, lookback, features)")
    names = tuple(feature_names)
    if sequences.shape[2] != len(names):
        raise ValueError("feature_names length must match sequence feature axis")
    baseline_pred = predict_fn(sequences)
    baseline = _array_metric(targets, baseline_pred, task, metric)
    rng = np.random.default_rng(random_state)
    importances: list[tuple[str, float]] = []
    for feature_index, name in enumerate(names):
        deltas: list[float] = []
        for _ in range(n_repeats):
            perturbed = sequences.copy()
            # Permute the feature channel across the batch axis only.
            order = rng.permutation(perturbed.shape[0])
            perturbed[:, :, feature_index] = perturbed[order, :, feature_index]
            permuted_pred = predict_fn(perturbed)
            permuted = _array_metric(targets, permuted_pred, task, metric)
            deltas.append(_degradation(baseline, permuted, metric))
        importances.append((name, float(np.mean(deltas))))
    ranked = tuple(sorted(importances, key=lambda item: item[1], reverse=True))
    return FeatureImportanceResult(
        model_name=model_name,
        method="lstm_permutation_sequence_sensitivity",
        task=task,
        importances=ranked,
        notes=(
            "permutation-based sequence feature sensitivity",
            "measures predictive degradation when one feature channel is shuffled",
            "this is a sensitivity measure, not causal attribution",
            "do not interpret as LSTM feature importance in a causal sense",
            f"baseline_{metric}={baseline}",
        ),
    )


def _score(predict_fn, X, y, task, metric, probabilities_fn) -> float:
    predicted = np.asarray(predict_fn(X))
    actual = np.asarray(y)
    if task == "regression":
        metrics = evaluate_regression(actual, predicted)
        if metric not in metrics:
            raise ValueError(f"unsupported regression metric: {metric}")
        return float(metrics[metric])
    probabilities = None if probabilities_fn is None else np.asarray(probabilities_fn(X))
    metrics = evaluate_classification(actual, predicted, probabilities)
    if metric not in metrics or metrics[metric] is None:
        raise ValueError(f"unsupported classification metric: {metric}")
    return float(metrics[metric])


def _array_metric(actual, predicted, task, metric) -> float:
    if task == "regression":
        return float(evaluate_regression(actual, predicted)[metric])
    class_pred = (np.asarray(predicted) >= 0.5).astype(int) if predicted.dtype.kind == "f" else predicted
    return float(evaluate_classification(actual, class_pred)[metric])


def _degradation(baseline: float, permuted: float, metric: str) -> float:
    # For error metrics, higher after permutation is worse => positive importance.
    # For score metrics (accuracy, r2, f1), lower after permutation is worse.
    if metric in {"mae", "mse", "rmse"}:
        return float(permuted - baseline)
    return float(baseline - permuted)
