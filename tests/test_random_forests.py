import numpy as np
import pandas as pd

from ml.models.ensemble import RandomForestClassificationModel, RandomForestRegressionModel


def test_random_forest_regression_is_reproducible() -> None:
    X = pd.DataFrame({"feature": np.arange(20, dtype=float)})
    y = pd.Series(np.arange(20, dtype=float) ** 2)

    first = RandomForestRegressionModel(n_estimators=10).fit(X, y).predict(X)
    second = RandomForestRegressionModel(n_estimators=10).fit(X, y).predict(X)

    assert np.array_equal(first, second)


def test_random_forest_classifier_is_reproducible() -> None:
    X = pd.DataFrame({"feature": np.arange(20, dtype=float)})
    y = pd.Series([0, 1] * 10)

    first_model = RandomForestClassificationModel(n_estimators=10).fit(X, y)
    second_model = RandomForestClassificationModel(n_estimators=10).fit(X, y)

    assert np.array_equal(first_model.predict(X), second_model.predict(X))
    assert np.allclose(first_model.predict_proba(X), second_model.predict_proba(X))