"""Deterministic gradient-boosting baseline wrappers."""

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor


class GradientBoostingRegressionModel:
    """Gradient boosting regression baseline."""

    name = "gradient_boosting_regression"

    def __init__(self, random_state: int = 42) -> None:
        self.model = GradientBoostingRegressor(random_state=random_state)

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> "GradientBoostingRegressionModel":
        self.model.fit(X_train, y_train)
        self.feature_names_ = tuple(X_train.columns)
        return self

    def predict(self, X: pd.DataFrame):
        self._validate_columns(X)
        return self.model.predict(X)

    def _validate_columns(self, X: pd.DataFrame) -> None:
        if not hasattr(self, "feature_names_"):
            raise RuntimeError("model must be fitted before prediction")
        if tuple(X.columns) != self.feature_names_:
            raise ValueError("feature columns do not match training columns")


class GradientBoostingClassificationModel:
    """Gradient boosting classification baseline."""

    name = "gradient_boosting_classifier"

    def __init__(self, random_state: int = 42) -> None:
        self.model = GradientBoostingClassifier(random_state=random_state)

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
    ) -> "GradientBoostingClassificationModel":
        self.model.fit(X_train, y_train)
        self.feature_names_ = tuple(X_train.columns)
        return self

    def predict(self, X: pd.DataFrame):
        self._validate_columns(X)
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame):
        self._validate_columns(X)
        return self.model.predict_proba(X)

    def _validate_columns(self, X: pd.DataFrame) -> None:
        if not hasattr(self, "feature_names_"):
            raise RuntimeError("model must be fitted before prediction")
        if tuple(X.columns) != self.feature_names_:
            raise ValueError("feature columns do not match training columns")