"""Validation of temporal supervised-dataset boundaries."""

import pandas as pd

from ml.splitting import TemporalSplit


class SplitValidationError(ValueError):
    """Raised when temporal dataset splits violate integrity rules."""


def validate_temporal_split(split: TemporalSplit) -> None:
    """Validate chronology, disjointness, alignment, and feature consistency."""
    frames = (split.train, split.validation, split.test)
    feature_names = frames[0].feature_names
    for frame in frames:
        if len(frame.X) != len(frame.y) or len(frame.X) != len(frame.dates):
            raise SplitValidationError("X, y, and dates must have matching lengths")
        if tuple(frame.X.columns) != feature_names or frame.feature_names != feature_names:
            raise SplitValidationError("all splits must have identical feature columns")
        dates = pd.to_datetime(frame.dates, errors="coerce")
        if dates.isna().any() or dates.duplicated().any() or not dates.is_monotonic_increasing:
            raise SplitValidationError("split dates must be valid, unique, and ordered")

    train_dates = pd.to_datetime(split.train.dates)
    validation_dates = pd.to_datetime(split.validation.dates)
    test_dates = pd.to_datetime(split.test.dates)
    if not train_dates.max() < validation_dates.min():
        raise SplitValidationError("train dates must precede validation dates")
    if not validation_dates.max() < test_dates.min():
        raise SplitValidationError("validation dates must precede test dates")
    all_dates = pd.concat([train_dates, validation_dates, test_dates], ignore_index=True)
    if all_dates.duplicated().any():
        raise SplitValidationError("split dates must not overlap")