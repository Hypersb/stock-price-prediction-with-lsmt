import numpy as np
import pandas as pd

from ml.validation.baselines import evaluate_baselines_walk_forward
from ml.validation.config import WalkForwardConfig
from ml.validation.folds import generate_expanding_folds


def test_baseline_walk_forward_evaluates_all_regression_models() -> None:
    X = pd.DataFrame({"feature": np.arange(18, dtype=float)})
    y = pd.Series(np.linspace(-0.1, 0.1, 18))
    dates = pd.date_range("2020-01-01", periods=18)
    config = WalkForwardConfig(initial_train_size=8, validation_size=3, test_size=3, step_size=3)

    results = evaluate_baselines_walk_forward(
        X, y, dates, generate_expanding_folds(18, config), task="regression", config=config
    )

    assert len(results) == 8
    assert {result.model_name for result in results} == {
        "naive_regression", "linear_regression", "random_forest_regression", "gradient_boosting_regression"
    }
    assert all(len(result.dates) == 3 for result in results)