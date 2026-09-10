import numpy as np
import pandas as pd

from ml.boundaries import prepare_model_ready
from ml.dataset import assemble_supervised


def test_boundaries_remove_warmup_and_target_tail_transparently() -> None:
    dates = pd.Series(pd.date_range("2020-01-01", periods=5))
    features = pd.DataFrame(
        {"date": dates, "feature": [np.nan, 1.0, 2.0, 3.0, 4.0]}
    )
    targets = pd.DataFrame({"future_return_1": [0.1, 0.2, 0.3, 0.4, np.nan]})
    frame = assemble_supervised(features, targets, "future_return_1")

    result = prepare_model_ready(frame)

    assert result.frame.dates.tolist() == list(dates.iloc[1:4])
    assert result.feature_warmup_rows == 1
    assert result.target_tail_rows == 1
    assert result.overlapping_missing_rows == 0
    assert result.removed_dates.tolist() == [dates.iloc[0], dates.iloc[4]]