"""Date-aware lookback sequence construction."""

import numpy as np
import pandas as pd

from ml.neural.sequences import create_sequences


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