"""Date-aware lookback sequence construction."""

import numpy as np
import pandas as pd

from ml.neural.sequences import create_sequences, validate_lookback


def create_dated_sequences(
    X: pd.DataFrame | np.ndarray,
    y: pd.Series | np.ndarray,
    dates: pd.Series | pd.Index,
    lookback: int,
) -> tuple[np.ndarray, np.ndarray, pd.DatetimeIndex]:
    """Create sequences and preserve the date belonging to each target row."""
    date_index = pd.DatetimeIndex(pd.to_datetime(dates, errors="coerce"))
    if len(date_index) != len(y):
        raise ValueError("dates and targets must have matching lengths")
    if date_index.isna().any() or date_index.has_duplicates or not date_index.is_monotonic_increasing:
        raise ValueError("dates must be valid, unique, and chronological")
    sequences, targets = create_sequences(X, y, lookback)
    target_dates = date_index[lookback - 1 :]
    if len(target_dates) != len(targets):
        raise ValueError("sequence targets and dates must remain aligned")
    return sequences, targets, target_dates


def create_dated_sequences_with_context(
    context_X: pd.DataFrame | np.ndarray | None,
    partition_X: pd.DataFrame | np.ndarray,
    partition_y: pd.Series | np.ndarray,
    partition_dates: pd.Series | pd.Index,
    lookback: int,
) -> tuple[np.ndarray, np.ndarray, pd.DatetimeIndex]:
    """Build partition sequences using earlier feature rows as lookback context.

    Targets and target dates come only from the evaluation partition. Feature
    windows may include chronologically earlier rows from ``context_X`` that
    occurred before each target time. Targets from the context partition never
    enter the returned target vector.
    """
    validate_lookback(lookback)
    date_index = pd.DatetimeIndex(pd.to_datetime(partition_dates, errors="coerce"))
    partition_features = np.asarray(partition_X, dtype=np.float32)
    targets = np.asarray(partition_y, dtype=np.float32)
    if partition_features.ndim != 2:
        raise ValueError("partition_X must be a two-dimensional feature matrix")
    if targets.ndim != 1:
        raise ValueError("partition_y must be a one-dimensional target vector")
    if len(partition_features) != len(targets) or len(date_index) != len(targets):
        raise ValueError("partition features, targets, and dates must match")
    if (
        date_index.isna().any()
        or date_index.has_duplicates
        or not date_index.is_monotonic_increasing
    ):
        raise ValueError("dates must be valid, unique, and chronological")

    if context_X is None or (hasattr(context_X, "__len__") and len(context_X) == 0):
        context_features = np.empty((0, partition_features.shape[1]), dtype=np.float32)
    else:
        context_features = np.asarray(context_X, dtype=np.float32)
        if context_features.ndim != 2:
            raise ValueError("context_X must be a two-dimensional feature matrix")
        if context_features.shape[1] != partition_features.shape[1]:
            raise ValueError("context and partition feature widths must match")

    features = (
        partition_features
        if len(context_features) == 0
        else np.concatenate([context_features, partition_features], axis=0)
    )
    context_len = len(context_features)
    if len(features) < lookback:
        raise ValueError("not enough observations for the requested lookback")

    sequences: list[np.ndarray] = []
    aligned_targets: list[float] = []
    aligned_dates: list[pd.Timestamp] = []
    for local_index in range(len(targets)):
        global_index = context_len + local_index
        if global_index < lookback - 1:
            continue
        sequences.append(features[global_index - lookback + 1 : global_index + 1])
        aligned_targets.append(float(targets[local_index]))
        aligned_dates.append(date_index[local_index])

    if not sequences:
        raise ValueError("not enough observations for the requested lookback")
    return (
        np.stack(sequences).astype(np.float32),
        np.asarray(aligned_targets, dtype=np.float32),
        pd.DatetimeIndex(aligned_dates),
    )
