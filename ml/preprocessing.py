"""Train-only preprocessing for supervised feature matrices."""

from dataclasses import dataclass

import pandas as pd
from sklearn.preprocessing import StandardScaler


@dataclass
class TrainOnlyScaler:
    """Fit a StandardScaler on training data and reuse it for later splits."""

    scaler: StandardScaler
    feature_names: tuple[str, ...] | None = None

    @classmethod
    def create(cls) -> "TrainOnlyScaler":
        return cls(scaler=StandardScaler())

    def fit(self, X_train: pd.DataFrame) -> "TrainOnlyScaler":
        """Fit scaling parameters using training rows only."""
        self.feature_names = tuple(X_train.columns)
        self.scaler.fit(X_train)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform a split using parameters learned from training data."""
        if self.feature_names is None:
            raise RuntimeError("scaler must be fitted on training data first")
        if tuple(X.columns) != self.feature_names:
            raise ValueError("feature columns do not match fitted training columns")
        return pd.DataFrame(self.scaler.transform(X), index=X.index, columns=self.feature_names)

    def fit_transform(self, X_train: pd.DataFrame) -> pd.DataFrame:
        """Fit on training rows and transform those same rows."""
        self.fit(X_train)
        return self.transform(X_train)