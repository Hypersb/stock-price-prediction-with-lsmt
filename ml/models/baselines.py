"""Naive predictive baselines for supervised market datasets."""

import numpy as np
import pandas as pd


class NaiveRegression:
    """Predict zero future return for every observation."""

    name = "naive_regression"

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None) -> "NaiveRegression":
        """Accept training data without estimating parameters."""
        if not hasattr(X, "__len__"):
            raise TypeError("X must be a sized feature matrix")
        self.is_fitted_ = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Return a zero future-return prediction for each row."""
        if not getattr(self, "is_fitted_", False):
            raise RuntimeError("model must be fitted before prediction")
        return np.zeros(len(X), dtype=float)


class NaiveDirection:
    """Predict the majority direction learned from training labels."""

    name = "naive_direction"

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "NaiveDirection":
        """Learn the majority class from training labels only."""
        labels = pd.Series(y).dropna()
        if labels.empty or not labels.isin([0, 1]).all():
            raise ValueError("training labels must contain non-empty binary values")
        counts = labels.value_counts()
        self.majority_class_ = int(counts.sort_index().idxmax())
        self.is_fitted_ = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Return the learned majority class for each row."""
        if not getattr(self, "is_fitted_", False):
            raise RuntimeError("model must be fitted before prediction")
        return np.full(len(X), self.majority_class_, dtype=int)