"""Tests for model complexity comparison."""

import numpy as np
import pandas as pd

from ml.neural.lstm import LSTMRegressor
from ml.research.complexity import compare_model_complexity, count_trainable_parameters
from ml.training.config import TrainingConfig


def test_count_trainable_parameters_for_lstm() -> None:
    model = LSTMRegressor(input_size=3, hidden_size=4, num_layers=1)
    assert count_trainable_parameters(model) > 0


def test_complexity_comparison_includes_all_families() -> None:
    rng = np.random.default_rng(0)
    X_train = pd.DataFrame(rng.normal(size=(60, 3)), columns=["a", "b", "c"])
    y_train = pd.Series(X_train["a"] * 0.5 + rng.normal(scale=0.1, size=60))
    X_validation = pd.DataFrame(rng.normal(size=(30, 3)), columns=["a", "b", "c"])
    y_validation = pd.Series(X_validation["a"] * 0.5 + rng.normal(scale=0.1, size=30))

    result = compare_model_complexity(
        X_train,
        y_train,
        X_validation,
        y_validation,
        task="regression",
        lookback=3,
        hidden_size=4,
        training_config=TrainingConfig(epochs=1, patience=1, device="cpu", seed=1),
    )

    names = [row.model_name for row in result.rows]
    assert names == [
        "naive_regression",
        "linear_regression",
        "random_forest_regression",
        "gradient_boosting_regression",
        "lstm",
    ]
    lstm_row = result.rows[-1]
    assert lstm_row.parameter_count is not None and lstm_row.parameter_count > 0
    assert lstm_row.lookback_required == 3
    assert any("approximate" in note for note in result.notes)
    assert all(row.training_seconds >= 0 for row in result.rows)
