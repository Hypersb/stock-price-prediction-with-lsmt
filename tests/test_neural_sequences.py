import numpy as np
import pandas as pd
import pytest

from ml.neural.sequences import create_sequences


def test_sequences_align_window_end_with_target() -> None:
    X = pd.DataFrame({"feature": [0, 1, 2, 3, 4]})
    y = pd.Series([10, 11, 12, 13, 14])

    sequences, targets = create_sequences(X, y, lookback=3)

    assert sequences.shape == (3, 3, 1)
    assert targets.tolist() == [12.0, 13.0, 14.0]
    assert sequences[:, :, 0].tolist() == [[0, 1, 2], [1, 2, 3], [2, 3, 4]]


@pytest.mark.parametrize("lookback", [0, -1, True])
def test_sequences_reject_invalid_lookback(lookback) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        create_sequences(np.ones((2, 1)), np.ones(2), lookback)


def test_sequences_reject_insufficient_history() -> None:
    with pytest.raises(ValueError, match="not enough"):
        create_sequences(np.ones((2, 1)), np.ones(2), lookback=3)