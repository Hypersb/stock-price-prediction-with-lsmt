"""Regression model wrappers for baseline experiments."""

import pandas as pd
from sklearn.linear_model import LinearRegression


class LinearRegressionModel:
    """Thin wrapper around scikit-learn linear regression."""

    name = "linear_regression"

    def __init__(self) -> None:
        self.model = LinearRegression()

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> "LinearRegressionModel":
        """Fit only on the supplied training partition."""
        self.model.fit(X_train, y_train)
        self.feature_names_ = tuple(X_train.columns)
        return self

    def predict(self, X: pd.DataFrame):
        """Predict returns for a feature matrix."""
        self._validate_columns(X)
        return self.model.predict(X)

    def _validate_columns(self, X: pd.DataFrame) -> None:
        if not hasattr(self, "feature_names_"):
            raise RuntimeError("model must be fitted before prediction")
        if tuple(X.columns) != self.feature_names_:
            raise ValueError("feature columns do not match training columns")