import numpy as np
import pandas as pd

from ml.models.regression import LinearRegressionModel


def test_linear_regression_fits_and_predicts() -> None:
    X = pd.DataFrame({"feature": [0.0, 1.0, 2.0, 3.0]})
    y = pd.Series([1.0, 3.0, 5.0, 7.0])
    model = LinearRegressionModel().fit(X, y)

    predictions = model.predict(pd.DataFrame({"feature": [4.0]}))

    assert np.isclose(predictions[0], 9.0)
    assert model.name == "linear_regression"