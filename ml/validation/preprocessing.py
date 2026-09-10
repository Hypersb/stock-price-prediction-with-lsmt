"""Fold-specific train-only preprocessing."""

from dataclasses import dataclass

import pandas as pd

from ml.preprocessing import TrainOnlyScaler


@dataclass(frozen=True)
class FoldPreprocessed:
    """Transformed matrices and the scaler fitted only on one fold's train data."""

    X_train: pd.DataFrame
    X_validation: pd.DataFrame
    X_test: pd.DataFrame
    preprocessor: TrainOnlyScaler


def preprocess_fold(
    X_train: pd.DataFrame,
    X_validation: pd.DataFrame,
    X_test: pd.DataFrame,
) -> FoldPreprocessed:
    """Fit a fresh scaler on X_train and transform the other partitions."""
    preprocessor = TrainOnlyScaler.create()
    return FoldPreprocessed(
        X_train=preprocessor.fit_transform(X_train),
        X_validation=preprocessor.transform(X_validation),
        X_test=preprocessor.transform(X_test),
        preprocessor=preprocessor,
    )