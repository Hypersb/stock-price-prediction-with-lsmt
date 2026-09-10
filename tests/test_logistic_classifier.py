import numpy as np
import pandas as pd

from ml.models.classification import LogisticDirectionModel


def test_logistic_classifier_predicts_labels_and_probabilities() -> None:
    X = pd.DataFrame({"feature": [-2.0, -1.0, 1.0, 2.0]})
    y = pd.Series([0, 0, 1, 1])
    model = LogisticDirectionModel().fit(X, y)

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)

    assert set(predictions) == {0, 1}
    assert probabilities.shape == (4, 2)
    assert np.allclose(probabilities.sum(axis=1), 1.0)
    assert model.name == "logistic_regression"