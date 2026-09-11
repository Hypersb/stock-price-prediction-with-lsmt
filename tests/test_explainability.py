"""Tests for model explainability utilities."""

import numpy as np
import pandas as pd
import pytest

from ml.models.ensemble import RandomForestRegressionModel
from ml.models.regression import LinearRegressionModel
from ml.research.explainability import (
    linear_coefficients,
    lstm_sequence_permutation_importance,
    permutation_importance,
    tree_native_importance,
)


def test_tree_native_importance_ranks_informative_feature() -> None:
    rng = np.random.default_rng(0)
    X = pd.DataFrame(
        {
            "signal": np.linspace(-1, 1, 80),
            "noise": rng.normal(size=80),
        }
    )
    y = pd.Series(X["signal"] * 2 + rng.normal(scale=0.05, size=80))
    model = RandomForestRegressionModel(n_estimators=30, random_state=0)
    model.fit(X, y)

    result = tree_native_importance(model, tuple(X.columns))

    assert result.method == "tree_native_impurity"
    assert result.importances[0][0] == "signal"
    assert result.importances[0][1] > result.importances[1][1]


def test_linear_coefficients_document_scaling_dependency() -> None:
    X = pd.DataFrame({"a": np.arange(20, dtype=float), "b": np.linspace(0, 1, 20)})
    y = pd.Series(2 * X["a"] + 0.1 * X["b"])
    model = LinearRegressionModel().fit(X, y)

    result = linear_coefficients(model, ("a", "b"), scaled_features=True)

    assert result.method == "linear_coefficients"
    assert any("standardized units" in note for note in result.notes)
    assert result.importances[0][0] == "a"


def test_permutation_importance_uses_evaluation_partition() -> None:
    rng = np.random.default_rng(1)
    X_train = pd.DataFrame({"signal": np.linspace(-1, 1, 60), "noise": rng.normal(size=60)})
    y_train = pd.Series(X_train["signal"] * 3)
    X_eval = pd.DataFrame({"signal": np.linspace(-1, 1, 40), "noise": rng.normal(size=40)})
    y_eval = pd.Series(X_eval["signal"] * 3)
    model = LinearRegressionModel().fit(X_train, y_train)

    result = permutation_importance(
        model.predict,
        X_eval,
        y_eval,
        model_name=model.name,
        task="regression",
        metric="rmse",
        n_repeats=4,
        random_state=3,
    )

    assert result.method == "permutation_importance"
    assert result.importances[0][0] == "signal"
    assert result.importances[0][1] > result.importances[1][1]


def test_lstm_sequence_sensitivity_is_explicitly_non_causal() -> None:
    rng = np.random.default_rng(2)
    sequences = rng.normal(size=(25, 4, 2))
    # Target depends only on feature 0 mean.
    targets = sequences[:, :, 0].mean(axis=1)

    def predict_fn(batch: np.ndarray) -> np.ndarray:
        return batch[:, :, 0].mean(axis=1)

    result = lstm_sequence_permutation_importance(
        sequences,
        targets,
        ("useful", "noise"),
        predict_fn,
        metric="rmse",
        n_repeats=5,
        random_state=4,
    )

    assert result.method == "lstm_permutation_sequence_sensitivity"
    assert any("not causal" in note for note in result.notes)
    assert result.importances[0][0] == "useful"


def test_tree_native_importance_rejects_linear_model() -> None:
    model = LinearRegressionModel().fit(
        pd.DataFrame({"a": [1.0, 2.0, 3.0]}),
        pd.Series([1.0, 2.0, 3.0]),
    )
    with pytest.raises(ValueError, match="feature_importances_"):
        tree_native_importance(model, ("a",))
