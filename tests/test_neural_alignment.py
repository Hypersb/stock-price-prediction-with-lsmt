import numpy as np
import pandas as pd

from ml.neural.alignment import create_dated_sequences


def test_dated_sequences_align_target_dates_to_window_end() -> None:
    dates = pd.date_range("2020-01-01", periods=5)
    sequences, targets, target_dates = create_dated_sequences(
        np.arange(5).reshape(-1, 1), np.arange(10, 15), dates, lookback=3
    )

    assert sequences.shape == (3, 3, 1)
    assert targets.tolist() == [12.0, 13.0, 14.0]
    assert target_dates.tolist() == list(dates[2:])