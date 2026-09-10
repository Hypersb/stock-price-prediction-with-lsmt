import numpy as np
import pandas as pd

from ml.training.config import TrainingConfig
from ml.validation.config import WalkForwardConfig
from ml.validation.folds import generate_expanding_folds
from ml.validation.lstm import evaluate_lstm_walk_forward


def test_lstm_walk_forward_runs_tiny_regression_fold() -> None:
    X = pd.DataFrame({"feature": np.linspace(0.0, 1.0, 30)})
    y = pd.Series(np.linspace(-0.1, 0.1, 30))
    dates = pd.date_range("2020-01-01", periods=30)
    config = WalkForwardConfig(initial_train_size=12, validation_size=6, test_size=6, step_size=6)

    results = evaluate_lstm_walk_forward(
        X, y, dates, generate_expanding_folds(30, config), task="regression", config=config,
        lookback=3, hidden_size=4, training_config=TrainingConfig(epochs=1, patience=1, device="cpu")
    )

    assert len(results) == 2
    assert results[0].model_name == "lstm"
    assert len(results[0].dates) == 4