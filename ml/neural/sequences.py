"""Chronological lookback sequence construction."""

import numpy as np
import pandas as pd


def create_sequences(
    X: pd.DataFrame | np.ndarray,
    y: pd.Series | np.ndarray,
    lookback: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Create isolated trailing sequences aligned to their ending targets."""
    _validate_lookback(lookback)
    features = np.asarray(X, dtype=np.float32)
    targets = np.asarray(y, dtype=np.float32)
    if features.ndim != 2:
        raise ValueError("X must be a two-dimensional feature matrix")
    if targets.ndim != 1:
        raise ValueError("y must be a one-dimensional target vector")
    if len(features) != len(targets):
        raise ValueError("X and y must have matching lengths")
    if len(features) < lookback:
        raise ValueError("not enough observations for the requested lookback")
    sequences = np.stack(
        [features[index - lookback + 1 : index + 1] for index in range(lookback - 1, len(features))]
    )
    aligned_targets = targets[lookback - 1 :]
    return sequences, aligned_targets


def _validate_lookback(lookback: int) -> None:
    if isinstance(lookback, bool) or not isinstance(lookback, int) or lookback <= 0:
        raise ValueError("lookback must be a positive integer")