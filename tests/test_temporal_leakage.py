"""Temporal leakage regression tests for splits and news features."""

from __future__ import annotations

import pandas as pd

from ml.dataset import SupervisedFrame
from ml.splitting import chronological_split


def test_purged_split_prevents_horizon_overlap_into_next_partition() -> None:
    rows = 200
    frame = SupervisedFrame(
        X=pd.DataFrame({"f": range(rows)}),
        y=pd.Series(range(rows)),
        dates=pd.Series(pd.date_range("2018-01-01", periods=rows, freq="D")),
        feature_names=("f",),
    )
    horizon = 5
    split = chronological_split(frame, forecast_horizon=horizon)
    train_end_pos = len(split.train.X) - 1
    # Validation block still starts at the unpurged boundary index 140 for 70%.
    validation_start = int(rows * 0.70)
    assert train_end_pos + horizon < validation_start
    validation_end_pos = validation_start + len(split.validation.X) - 1
    test_start = validation_start + int(rows * 0.15)
    assert validation_end_pos + horizon < test_start
