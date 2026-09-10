"""Classification model wrappers for baseline experiments."""

import pandas as pd
from sklearn.linear_model import LogisticRegression


class LogisticDirectionModel:
    """Thin wrapper around scikit-learn logistic regression."""

    name = "logistic_regression"

    def __init__(self, max_iter: int = 1000) -> None:
        self.model = LogisticRegression(max_iter=max_iter, random_state=42)

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> "LogisticDirectionModel":
        """Fit only on the supplied training partition."""
        self.model.fit(X_train, y_train)
        self.feature_names_ = tuple(X_train.columns)
        return self

    def predict(self, X: pd.DataFrame):
        """Predict binary direction labels."""
        self._validate_columns(X)
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame):
        """Return class probabilities for a feature matrix."""
        self._validate_columns(X)
        return self.model.predict_proba(X)

    def _validate_columns(self, X: pd.DataFrame) -> None:
        if not hasattr(self, "feature_names_"):
            raise RuntimeError("model must be fitted before prediction")
        if tuple(X.columns) != self.feature_names_:
            raise ValueError("feature columns do not match training columns")