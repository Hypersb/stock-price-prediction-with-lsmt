"""Assembly of feature matrices and supervised targets."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SupervisedFrame:
    """Feature matrix, target vector, dates, and deterministic feature names."""

    X: pd.DataFrame
    y: pd.Series
    dates: pd.Series
    feature_names: tuple[str, ...]


def assemble_supervised(
    features: pd.DataFrame,
    targets: pd.DataFrame,
    target_column: str,
    *,
    include_ohlcv: bool = False,
) -> SupervisedFrame:
    """Separate features, one target, and dates without allowing target leakage."""
    if not isinstance(features, pd.DataFrame) or not isinstance(targets, pd.DataFrame):
        raise TypeError("features and targets must be pandas DataFrames")
    if "date" not in features.columns:
        raise ValueError("features must contain a date column")
    if target_column not in targets.columns:
        raise ValueError(f"target column is missing: {target_column}")
    if len(features) != len(targets):
        raise ValueError("features and targets must have matching row counts")
    if features.index.equals(targets.index) is False:
        raise ValueError("features and targets must have matching indexes")

    excluded = {"date", *targets.columns}
    if not include_ohlcv:
        excluded.update({"open", "high", "low", "close", "volume"})
    feature_names = tuple(column for column in features.columns if column not in excluded)
    if not feature_names:
        raise ValueError("no feature columns remain after exclusions")
    X = features.loc[:, feature_names].copy()
    y = targets[target_column].copy()
    dates = features["date"].copy()
    return SupervisedFrame(X=X, y=y, dates=dates, feature_names=feature_names)