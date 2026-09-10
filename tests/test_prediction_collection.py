import numpy as np
import pandas as pd

from ml.validation.baselines import WalkForwardModelResult
from ml.validation.predictions import collect_predictions


def test_prediction_collection_preserves_fold_identity_and_sorts_dates() -> None:
    results = [
        WalkForwardModelResult(2, "model", "regression", {}, pd.DatetimeIndex(["2020-01-02"]), np.array([2.0]), np.array([1.0])),
        WalkForwardModelResult(1, "model", "regression", {}, pd.DatetimeIndex(["2020-01-01"]), np.array([1.0]), np.array([0.0])),
    ]

    frame = collect_predictions(results)

    assert frame["date"].tolist() == list(pd.to_datetime(["2020-01-01", "2020-01-02"]))
    assert frame["fold"].tolist() == [1, 2]


def test_prediction_collection_keeps_overlapping_dates_explicit() -> None:
    result = WalkForwardModelResult(
        1, "model", "classification", {}, pd.DatetimeIndex(["2020-01-01"]), np.array([1]), np.array([1]), np.array([0.8])
    )

    frame = collect_predictions([result])

    assert frame.loc[0, "probability"] == 0.8
    assert frame.loc[0, "predicted_class"] == 1