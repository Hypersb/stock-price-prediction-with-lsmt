import pandas as pd
import pytest

from ml.dataset import SupervisedFrame
from ml.split_validation import SplitValidationError, validate_temporal_split
from ml.splitting import chronological_split


def split():
    dates = pd.Series(pd.date_range("2020-01-01", periods=20))
    frame = SupervisedFrame(
        X=pd.DataFrame({"feature": range(20)}),
        y=pd.Series(range(20)),
        dates=dates,
        feature_names=("feature",),
    )
    return chronological_split(frame)


def test_temporal_split_validation_accepts_valid_split() -> None:
    validate_temporal_split(split())


def test_temporal_split_validation_rejects_column_mismatch() -> None:
    valid = split()
    invalid_validation = SupervisedFrame(
        X=valid.validation.X.rename(columns={"feature": "other"}),
        y=valid.validation.y,
        dates=valid.validation.dates,
        feature_names=("other",),
    )
    invalid = type(valid)(valid.train, invalid_validation, valid.test)

    with pytest.raises(SplitValidationError, match="identical feature"):
        validate_temporal_split(invalid)