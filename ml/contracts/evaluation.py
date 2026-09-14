"""Evaluation metric name ownership (formulas live in ``ml.evaluation``)."""

from __future__ import annotations

from typing import Final

REGRESSION_METRIC_NAMES: Final[frozenset[str]] = frozenset(
    {"mae", "mse", "rmse", "r2", "directional_accuracy"}
)
CLASSIFICATION_METRIC_NAMES: Final[frozenset[str]] = frozenset(
    {
        "accuracy",
        "balanced_accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
    }
)
