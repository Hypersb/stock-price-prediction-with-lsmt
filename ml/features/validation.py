"""Validation checks for engineered feature frames."""

import re

import numpy as np
import pandas as pd


class FeatureValidationError(ValueError):
    """Raised when an engineered feature frame violates its contract."""


def validate_features(features: pd.DataFrame) -> None:
    """Validate chronology, numeric values, uniqueness, and scope of features."""
    if not isinstance(features, pd.DataFrame):
        raise FeatureValidationError("features must be a pandas DataFrame")
    if features.columns.duplicated().any():
        raise FeatureValidationError("feature columns must be unique")
    if "date" not in features.columns:
        raise FeatureValidationError("features must contain a date column")
    dates = pd.to_datetime(features["date"], errors="coerce")
    if dates.isna().any():
        raise FeatureValidationError("feature dates must be valid")
    if dates.duplicated().any():
        raise FeatureValidationError("feature dates must not contain duplicates")
    if not dates.is_monotonic_increasing:
        raise FeatureValidationError("feature dates must be chronological")

    forbidden = re.compile(r"(?i)(target|future|shift_-)")
    forbidden_columns = [column for column in features.columns if forbidden.search(str(column))]
    if forbidden_columns:
        raise FeatureValidationError(f"forbidden feature columns: {forbidden_columns}")
    numeric_columns = features.columns.difference(["date"])
    if not all(pd.api.types.is_numeric_dtype(features[column]) for column in numeric_columns):
        raise FeatureValidationError("all non-date feature columns must be numeric")
    if np.isinf(features[numeric_columns].to_numpy(dtype=float)).any():
        raise FeatureValidationError("features must not contain infinite values")