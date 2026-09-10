from dataclasses import replace

import numpy as np
import pandas as pd

from ml.comparison import compare_classification_models, compare_regression_models
from ml.supervised import SupervisedDataset


def dataset() -> SupervisedDataset:
    X_train = pd.DataFrame({"feature": np.arange(30, dtype=float)})
    X_validation = pd.DataFrame({"feature": np.arange(30, 40, dtype=float)})
    X_test = pd.DataFrame({"feature": np.arange(40, 50, dtype=float)})
    return SupervisedDataset(
        X_train=X_train,
        y_train=pd.Series(np.linspace(-0.1, 0.1, 30)),
        dates_train=pd.Series(pd.date_range("2020-01-01", periods=30)),
        X_validation=X_validation,
        y_validation=pd.Series(np.linspace(-0.05, 0.05, 10)),
        dates_validation=pd.Series(pd.date_range("2020-02-01", periods=10)),
        X_test=X_test,
        y_test=pd.Series(np.linspace(-0.04, 0.04, 10)),
        dates_test=pd.Series(pd.date_range("2020-03-01", periods=10)),
        feature_names=("feature",),
        preprocessor=None,
        metadata={},
    )


def test_comparison_returns_validation_results_for_all_regressors() -> None:
    results = compare_regression_models(dataset())

    assert [result.model_name for result in results] == [
        "naive_regression", "linear_regression", "random_forest_regression", "gradient_boosting_regression"
    ]
    assert all(result.dataset_split == "validation" for result in results)
    assert all("rmse" in result.metrics for result in results)


def test_comparison_returns_validation_results_for_all_classifiers() -> None:
    data = dataset()
    data = replace(
        data,
        y_train=pd.Series([0, 1] * 15),
        y_validation=pd.Series([0, 1] * 5),
    )

    results = compare_classification_models(data)

    assert len(results) == 4
    assert {result.task_type for result in results} == {"classification"}
    assert all("accuracy" in result.metrics for result in results)