"""Deterministic tree-ensemble baseline wrappers."""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


class RandomForestRegressionModel:
    """Random forest regression baseline with a fixed experiment seed."""

    name = "random_forest_regression"

    def __init__(self, n_estimators: int = 100, random_state: int = 42) -> None:
        self.model = RandomForestRegressor(
            n_estimators=n_estimators, random_state=random_state, n_jobs=1
        )

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> "RandomForestRegressionModel":
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


class RandomForestClassificationModel:
    """Random forest classification baseline with a fixed experiment seed."""

    name = "random_forest_classifier"

    def __init__(self, n_estimators: int = 100, random_state: int = 42) -> None:
        self.model = RandomForestClassifier(
            n_estimators=n_estimators, random_state=random_state, n_jobs=1
        )

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series) -> "RandomForestClassificationModel":
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