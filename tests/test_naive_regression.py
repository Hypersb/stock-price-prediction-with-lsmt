import numpy as np
import pandas as pd
import pytest

from ml.models.baselines import NaiveRegression


def test_naive_regression_predicts_zero_after_fit() -> None:
    model = NaiveRegression().fit(pd.DataFrame({"feature": [1.0, 2.0]}), pd.Series([0.1, -0.1]))

    predictions = model.predict(pd.DataFrame({"feature": [3.0, 4.0, 5.0]}))

    assert np.array_equal(predictions, np.zeros(3))


def test_naive_regression_requires_fit() -> None:
    with pytest.raises(RuntimeError, match="fitted"):
        NaiveRegression().predict(pd.DataFrame({"feature": [1.0]}))