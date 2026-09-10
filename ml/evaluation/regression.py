"""Regression evaluation metrics."""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_regression(y_true: pd.Series, y_pred: np.ndarray | pd.Series) -> dict[str, float]:
    """Calculate predictive regression metrics without economic interpretation."""
    actual = np.asarray(y_true, dtype=float)
    predicted = np.asarray(y_pred, dtype=float)
    if actual.shape != predicted.shape:
        raise ValueError("y_true and y_pred must have matching shapes")
    if len(actual) == 0:
        raise ValueError("evaluation data must not be empty")
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "mse": float(mean_squared_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)),
        "directional_accuracy": float(np.mean(np.sign(predicted) == np.sign(actual))),
    }