import pandas as pd

from ml.validation.config import WalkForwardConfig
from ml.validation.folds import generate_expanding_folds


def test_expanding_folds_grow_training_window() -> None:
    config = WalkForwardConfig(initial_train_size=5, validation_size=2, test_size=2, step_size=2)
    dates = pd.date_range("2020-01-01", periods=13)

    folds = generate_expanding_folds(13, config, dates)

    assert len(folds) == 2
    assert folds[0].train_indices.tolist() == [0, 1, 2, 3, 4]
    assert folds[0].validation_indices.tolist() == [5, 6]
    assert folds[0].test_indices.tolist() == [7, 8]
    assert folds[1].train_indices.tolist() == list(range(7))
    assert folds[1].test_dates[0] == dates[9]