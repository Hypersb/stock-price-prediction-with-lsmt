import pandas as pd
import pytest

from ml.dataset import SupervisedFrame
from ml.splitting import chronological_split


def frame(rows: int = 20) -> SupervisedFrame:
    dates = pd.Series(pd.date_range("2020-01-01", periods=rows))
    X = pd.DataFrame({"feature": range(rows)})
    y = pd.Series(range(rows), name="target")
    return SupervisedFrame(X=X, y=y, dates=dates, feature_names=("feature",))


def test_chronological_split_is_contiguous_and_ordered() -> None:
    result = chronological_split(frame())

    assert len(result.train.X) == 14
    assert len(result.validation.X) == 3
    assert len(result.test.X) == 3
    assert result.train.dates.iloc[-1] < result.validation.dates.iloc[0]
    assert result.validation.dates.iloc[-1] < result.test.dates.iloc[0]
    assert result.train.X.iloc[0, 0] == 0
    assert result.test.X.iloc[-1, 0] == 19


def test_chronological_split_rejects_invalid_fractions_and_small_data() -> None:
    with pytest.raises(ValueError, match="sum to 1"):
        chronological_split(frame(), 0.5, 0.5, 0.5)
    with pytest.raises(ValueError, match="too small"):
        chronological_split(frame(2))