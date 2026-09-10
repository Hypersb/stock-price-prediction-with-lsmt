import numpy as np
import pandas as pd

from ml.neural.alignment import create_dated_sequences
from ml.neural.validation import validate_sequences


def test_sequences_are_invariant_to_observations_after_target() -> None:
    dates = pd.date_range("2020-01-01", periods=6)
    values = np.arange(6, dtype=float).reshape(-1, 1)
    targets = np.arange(10, 16, dtype=float)
    first_sequences, first_targets, first_dates = create_dated_sequences(values[:4], targets[:4], dates[:4], 3)
    extended_values = values.copy()
    extended_values[4:] = 1000
    second_sequences, second_targets, second_dates = create_dated_sequences(extended_values, targets, dates, 3)

    np.testing.assert_array_equal(first_sequences, second_sequences[:2])
    np.testing.assert_array_equal(first_targets, second_targets[:2])
    assert first_dates.equals(second_dates[:2])


def test_validate_sequences_accepts_finite_aligned_data() -> None:
    dates = pd.DatetimeIndex(pd.date_range("2020-01-01", periods=2))
    validate_sequences(np.ones((2, 3, 1)), np.ones(2), dates, 3, 1)