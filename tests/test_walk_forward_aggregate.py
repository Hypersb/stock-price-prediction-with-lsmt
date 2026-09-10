import numpy as np
import pandas as pd

from ml.validation.aggregate import aggregate_fold_results
from ml.validation.baselines import WalkForwardModelResult


def test_aggregate_fold_results_reports_stability_statistics() -> None:
    result = WalkForwardModelResult(
        fold=1,
        model_name="naive_regression",
        task="regression",
        metrics={"rmse": 1.0, "mae": 0.5},
        dates=pd.DatetimeIndex(["2020-01-01"]),
        actual=np.array([1.0]),
        predicted=np.array([0.0]),
    )
    second = WalkForwardModelResult(
        fold=2,
        model_name="naive_regression",
        task="regression",
        metrics={"rmse": 3.0, "mae": 1.5},
        dates=pd.DatetimeIndex(["2020-02-01"]),
        actual=np.array([1.0]),
        predicted=np.array([0.0]),
    )

    summary = aggregate_fold_results([result, second])[0]

    assert summary.fold_count == 2
    assert summary.metrics["rmse"] == {"mean": 2.0, "std": 1.0, "min": 1.0, "max": 3.0}