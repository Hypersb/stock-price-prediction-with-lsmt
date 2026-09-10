import numpy as np
import pandas as pd
import pytest

from ml.targets.validation import TargetValidationError, validate_targets


def test_target_validation_accepts_valid_regression_target() -> None:
    targets = pd.DataFrame({"future_return_2": [0.1, 0.2, np.nan, np.nan]})
    dates = pd.Series(pd.date_range("2020-01-01", periods=4))

    validate_targets(targets, "regression", 2, dates)


@pytest.mark.parametrize(
    "targets, target_type, horizon, message",
    [
        (pd.DataFrame({"direction_1": [1, 2, pd.NA]}), "direction", 1, "only 0 or 1"),
        (pd.DataFrame({"future_return_1": [0.1, np.inf, np.nan]}), "regression", 1, "infinite"),
        (pd.DataFrame({"future_return_1": [np.nan, 0.1]}), "regression", 1, "final horizon"),
        (pd.DataFrame({"wrong": [0.1, np.nan]}), "regression", 1, "expected target"),
    ],
)
def test_target_validation_rejects_invalid_targets(targets, target_type, horizon, message: str) -> None:
    with pytest.raises(TargetValidationError, match=message):
        validate_targets(targets, target_type, horizon)