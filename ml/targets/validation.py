"""Integrity validation for supervised-learning targets."""

import pandas as pd


class TargetValidationError(ValueError):
    """Raised when target data violates the supervised-data contract."""


def validate_targets(
    targets: pd.DataFrame,
    target_type: str,
    horizon: int,
    dates: pd.Series | None = None,
) -> None:
    """Validate target names, values, chronology, and unavailable tail rows."""
    if target_type not in {"regression", "direction"}:
        raise TargetValidationError("target_type must be 'regression' or 'direction'")
    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
        raise TargetValidationError("horizon must be a positive integer")
    if not isinstance(targets, pd.DataFrame) or len(targets.columns) != 1:
        raise TargetValidationError("targets must be a one-column pandas DataFrame")

    expected_name = f"future_return_{horizon}" if target_type == "regression" else f"direction_{horizon}"
    if list(targets.columns) != [expected_name]:
        raise TargetValidationError(f"expected target column: {expected_name}")
    values = targets.iloc[:, 0]
    if values.iloc[:-horizon].isna().any() or values.iloc[-horizon:].notna().any():
        raise TargetValidationError("only the final horizon rows may have missing targets")
    non_null = values.dropna()
    if target_type == "direction" and not non_null.isin([0, 1]).all():
        raise TargetValidationError("direction targets must contain only 0 or 1")
    if target_type == "regression" and not pd.api.types.is_numeric_dtype(non_null):
        raise TargetValidationError("future return targets must be numeric")
    if pd.api.types.is_numeric_dtype(non_null) and not pd.Series(non_null).replace(
        [float("inf"), float("-inf")], pd.NA
    ).notna().all():
        raise TargetValidationError("targets must not contain infinite values")

    if dates is not None:
        if not isinstance(dates, pd.Series):
            raise TargetValidationError("dates must be a pandas Series")
        parsed_dates = pd.to_datetime(dates, errors="coerce")
        if len(parsed_dates) != len(targets) or parsed_dates.isna().any():
            raise TargetValidationError("target dates must be valid and aligned")
        if parsed_dates.duplicated().any() or not parsed_dates.is_monotonic_increasing:
            raise TargetValidationError("target dates must be unique and chronological")