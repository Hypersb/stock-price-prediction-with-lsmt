import numpy as np
import pandas as pd
import pytest

from ml.features.pipeline import build_features
from ml.features.validation import FeatureValidationError, validate_features


def ohlcv(rows: int) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    close = np.arange(100.0, 100.0 + rows)
    return pd.DataFrame(
        {
            "date": dates,
            "open": close - 0.5,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": np.arange(1000, 1000 + rows),
        }
    )


def test_prefix_invariance_for_future_rows() -> None:
    short = build_features(ohlcv(40), moving_average_windows=(3,), ema_spans=(3,))
    extended = build_features(ohlcv(50), moving_average_windows=(3,), ema_spans=(3,))
    shared_columns = list(short.columns)
    shared = extended.iloc[: len(short)][shared_columns]

    pd.testing.assert_frame_equal(short, shared, check_exact=False, rtol=1e-12, atol=1e-12)


def test_feature_validation_accepts_pipeline_output() -> None:
    validate_features(build_features(ohlcv(40), moving_average_windows=(3,), ema_spans=(3,)))


@pytest.mark.parametrize(
    "mutator, message",
    [
        (lambda frame: frame.assign(target_return=1.0), "forbidden"),
        (lambda frame: frame.assign(bad=np.inf), "infinite"),
        (lambda frame: frame.iloc[::-1], "chronological"),
    ],
)
def test_feature_validation_rejects_scope_and_quality_issues(mutator, message: str) -> None:
    frame = build_features(ohlcv(40), moving_average_windows=(3,), ema_spans=(3,))

    with pytest.raises(FeatureValidationError, match=message):
        validate_features(mutator(frame))