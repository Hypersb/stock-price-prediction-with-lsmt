import numpy as np
import pandas as pd

from ml.neural.alignment import (
    create_dated_sequences,
    create_dated_sequences_with_context,
)


def test_dated_sequences_align_target_dates_to_window_end() -> None:
    dates = pd.date_range("2020-01-01", periods=5)
    sequences, targets, target_dates = create_dated_sequences(
        np.arange(5).reshape(-1, 1), np.arange(10, 15), dates, lookback=3
    )

    assert sequences.shape == (3, 3, 1)
    assert targets.tolist() == [12.0, 13.0, 14.0]
    assert target_dates.tolist() == list(dates[2:])


def test_context_sequences_recover_early_partition_targets() -> None:
    context = np.arange(4).reshape(-1, 1).astype(np.float32)
    partition = np.arange(4, 7).reshape(-1, 1).astype(np.float32)
    targets = np.array([100.0, 101.0, 102.0], dtype=np.float32)
    dates = pd.date_range("2020-01-05", periods=3)

    sequences, aligned, target_dates = create_dated_sequences_with_context(
        context, partition, targets, dates, lookback=3
    )

    assert len(aligned) == 3
    assert aligned.tolist() == [100.0, 101.0, 102.0]
    assert target_dates.tolist() == list(dates)
    # First partition target uses last two context rows + first partition row.
    np.testing.assert_array_equal(sequences[0].ravel(), [2.0, 3.0, 4.0])
    np.testing.assert_array_equal(sequences[-1].ravel(), [4.0, 5.0, 6.0])


def test_context_sequences_never_emit_context_targets() -> None:
    context = np.ones((5, 1), dtype=np.float32) * 9.0
    partition = np.arange(3).reshape(-1, 1).astype(np.float32)
    targets = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    dates = pd.date_range("2020-02-01", periods=3)
    _, aligned, _ = create_dated_sequences_with_context(
        context, partition, targets, dates, lookback=3
    )
    assert aligned.tolist() == [1.0, 2.0, 3.0]
