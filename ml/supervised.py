"""End-to-end supervised dataset construction without model training."""

from dataclasses import dataclass

import pandas as pd

from ml.boundaries import BoundaryResult, prepare_model_ready
from ml.data.validation import validate_ohlcv
from ml.dataset import assemble_supervised
from ml.features.pipeline import build_features
from ml.features.validation import validate_features
from ml.preprocessing import TrainOnlyScaler
from ml.split_validation import validate_temporal_split
from ml.splitting import TemporalSplit, chronological_split
from ml.targets.direction import direction_targets
from ml.targets.returns import future_return_targets
from ml.targets.validation import validate_targets


@dataclass(frozen=True)
class SupervisedDataset:
    """Model-ready chronological datasets and construction metadata."""

    X_train: pd.DataFrame
    y_train: pd.Series
    dates_train: pd.Series
    X_validation: pd.DataFrame
    y_validation: pd.Series
    dates_validation: pd.Series
    X_test: pd.DataFrame
    y_test: pd.Series
    dates_test: pd.Series
    feature_names: tuple[str, ...]
    preprocessor: TrainOnlyScaler
    metadata: dict[str, object]


def build_supervised_dataset(
    ohlcv: pd.DataFrame,
    *,
    target_type: str = "regression",
    horizon: int = 1,
    include_ohlcv: bool = False,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
    test_fraction: float = 0.15,
    feature_parameters: dict[str, object] | None = None,
) -> SupervisedDataset:
    """Construct, split, and scale a chronological supervised dataset."""
    validate_ohlcv(ohlcv)
    feature_kwargs = feature_parameters or {}
    features = build_features(ohlcv, **feature_kwargs)
    validate_features(features)
    if target_type == "regression":
        targets = future_return_targets(ohlcv["close"].reset_index(drop=True), [horizon])
        target_column = f"future_return_{horizon}"
    elif target_type == "direction":
        targets = direction_targets(ohlcv["close"].reset_index(drop=True), [horizon])
        target_column = f"direction_{horizon}"
    else:
        raise ValueError("target_type must be 'regression' or 'direction'")
    validate_targets(targets, target_type, horizon, ohlcv["date"].reset_index(drop=True))

    assembled = assemble_supervised(
        features,
        targets,
        target_column,
        include_ohlcv=include_ohlcv,
    )
    boundaries = prepare_model_ready(assembled)
    split = chronological_split(
        boundaries.frame,
        train_fraction,
        validation_fraction,
        test_fraction,
        forecast_horizon=horizon,
    )
    validate_temporal_split(split)
    preprocessor = TrainOnlyScaler.create()
    X_train = preprocessor.fit_transform(split.train.X)
    X_validation = preprocessor.transform(split.validation.X)
    X_test = preprocessor.transform(split.test.X)
    metadata = _metadata(target_type, horizon, boundaries, split)
    return SupervisedDataset(
        X_train=X_train,
        y_train=split.train.y,
        dates_train=split.train.dates,
        X_validation=X_validation,
        y_validation=split.validation.y,
        dates_validation=split.validation.dates,
        X_test=X_test,
        y_test=split.test.y,
        dates_test=split.test.dates,
        feature_names=split.train.feature_names,
        preprocessor=preprocessor,
        metadata=metadata,
    )


def _metadata(
    target_type: str,
    horizon: int,
    boundaries: BoundaryResult,
    split: TemporalSplit,
) -> dict[str, object]:
    return {
        "target_type": target_type,
        "horizon": horizon,
        "feature_warmup_rows": boundaries.feature_warmup_rows,
        "target_tail_rows": boundaries.target_tail_rows,
        "overlapping_missing_rows": boundaries.overlapping_missing_rows,
        "removed_rows": len(boundaries.removed_dates),
        "feature_count": len(split.train.feature_names),
        "train_rows": len(split.train.X),
        "validation_rows": len(split.validation.X),
        "test_rows": len(split.test.X),
    }