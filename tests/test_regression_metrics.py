import numpy as np

from ml.evaluation.regression import evaluate_regression


def test_regression_metrics_are_mathematically_correct() -> None:
    metrics = evaluate_regression(np.array([1.0, -1.0, 0.0]), np.array([1.0, 0.0, -1.0]))

    assert metrics["mae"] == 2 / 3
    assert metrics["mse"] == 2 / 3
    assert np.isclose(metrics["rmse"], np.sqrt(2 / 3))
    assert np.isclose(metrics["directional_accuracy"], 1 / 3)