"""Binary classification evaluation metrics."""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_classification(
    y_true: pd.Series,
    y_pred: np.ndarray | pd.Series,
    probabilities: np.ndarray | None = None,
) -> dict[str, float | np.ndarray | None]:
    """Evaluate binary direction predictions with positive class convention 1."""
    actual = np.asarray(y_true)
    predicted = np.asarray(y_pred)
    if actual.shape != predicted.shape or len(actual) == 0:
        raise ValueError("classification labels must be non-empty and shape-aligned")
    if not set(np.unique(actual)).issubset({0, 1}) or not set(np.unique(predicted)).issubset({0, 1}):
        raise ValueError("classification labels must be binary 0 or 1")
    accuracy = float(accuracy_score(actual, predicted))
    balanced_accuracy = (
        accuracy
        if len(np.unique(actual)) == 1
        else float(balanced_accuracy_score(actual, predicted))
    )
    result: dict[str, float | np.ndarray | None] = {
        "accuracy": accuracy,
        "balanced_accuracy": balanced_accuracy,
        "precision": float(precision_score(actual, predicted, zero_division=0)),
        "recall": float(recall_score(actual, predicted, zero_division=0)),
        "f1": float(f1_score(actual, predicted, zero_division=0)),
        "confusion_matrix": confusion_matrix(actual, predicted, labels=[0, 1]),
        "roc_auc": None,
    }
    if probabilities is not None and len(np.unique(actual)) == 2:
        probability_array = np.asarray(probabilities)
        positive_probability = probability_array[:, 1] if probability_array.ndim == 2 else probability_array
        result["roc_auc"] = float(roc_auc_score(actual, positive_probability))
    return result