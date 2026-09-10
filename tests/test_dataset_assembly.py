import pandas as pd
import pytest

from ml.dataset import assemble_supervised


def test_assembly_separates_target_and_excludes_raw_ohlcv_by_default() -> None:
    features = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=2),
            "open": [1.0, 2.0],
            "close": [1.0, 2.0],
            "momentum_1": [None, 1.0],
            "future_return_1": [0.1, None],
        }
    )
    targets = features[["future_return_1"]].copy()

    result = assemble_supervised(features, targets, "future_return_1")

    assert result.feature_names == ("momentum_1",)
    assert list(result.X.columns) == ["momentum_1"]
    assert "future_return_1" not in result.X.columns
    assert result.dates.equals(features["date"])


def test_assembly_can_explicitly_include_raw_ohlcv() -> None:
    features = pd.DataFrame({"date": [1, 2], "close": [10.0, 11.0], "feature": [1.0, 2.0]})
    targets = pd.DataFrame({"direction_1": [1, 0]})

    result = assemble_supervised(features, targets, "direction_1", include_ohlcv=True)

    assert result.feature_names == ("close", "feature")


def test_assembly_rejects_mismatched_rows() -> None:
    features = pd.DataFrame({"date": [1, 2], "feature": [1.0, 2.0]})
    targets = pd.DataFrame({"target": [1.0]})

    with pytest.raises(ValueError, match="matching row counts"):
        assemble_supervised(features, targets, "target")