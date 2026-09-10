import numpy as np
import pandas as pd

from ml.models.boosting import (
    GradientBoostingClassificationModel,
    GradientBoostingRegressionModel,
)


def test_gradient_boosting_regression_is_reproducible() -> None:
    X = pd.DataFrame({"feature": np.arange(20, dtype=float)})
    y = pd.Series(np.arange(20, dtype=float) ** 2)

    first = GradientBoostingRegressionModel().fit(X, y).predict(X)
    second = GradientBoostingRegressionModel().fit(X, y).predict(X)

    assert np.array_equal(first, second)


def test_gradient_boosting_classifier_predicts_probabilities() -> None:
    X = pd.DataFrame({"feature": np.arange(20, dtype=float)})
    y = pd.Series([0] * 10 + [1] * 10)
    model = GradientBoostingClassificationModel().fit(X, y)

    assert model.predict(X).shape == (20,)
    assert model.predict_proba(X).shape == (20, 2)