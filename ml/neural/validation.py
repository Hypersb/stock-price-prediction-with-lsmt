"""Validation checks for temporal sequence inputs and outputs."""

import numpy as np
import pandas as pd


class SequenceValidationError(ValueError):
    """Raised when sequence data violates temporal integrity rules."""


def validate_sequences(
    sequences: np.ndarray,
    targets: np.ndarray,
    target_dates: pd.DatetimeIndex,
    lookback: int,
    feature_count: int,
) -> None:
    """Validate sequence dimensions, finite values, and target-date alignment."""
    if isinstance(lookback, bool) or not isinstance(lookback, int) or lookback <= 0:
        raise SequenceValidationError("lookback must be a positive integer")
    if sequences.ndim != 3 or sequences.shape[1:] != (lookback, feature_count):
        raise SequenceValidationError("sequence dimensions do not match configuration")
    if targets.ndim != 1 or len(sequences) != len(targets) or len(target_dates) != len(targets):
        raise SequenceValidationError("sequence targets and dates must be aligned")
    if not np.isfinite(sequences).all() or not np.isfinite(targets).all():
        raise SequenceValidationError("sequences and targets must be finite")
    if target_dates.has_duplicates or not target_dates.is_monotonic_increasing:
        raise SequenceValidationError("target dates must be unique and chronological")