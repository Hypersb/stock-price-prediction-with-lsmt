"""Tests for market-data quality, fingerprints, instruments, and purged splits."""

from __future__ import annotations

import pandas as pd
import pytest

from ml.data.fingerprint import build_dataset_spec, fingerprint_ohlcv
from ml.data.instruments import InstrumentRef, classify_instrument
from ml.data.normalize import normalize_ohlcv
from ml.data.validation import (
    MarketDataValidationError,
    assess_market_data_quality,
    validate_ohlcv,
)
from ml.dataset import SupervisedFrame
from ml.features.identity import build_feature_set_spec, feature_parameters_id
from ml.splitting import chronological_split


def _ohlcv(rows: int = 5) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=rows, freq="D"),
            "open": [100.0 + i for i in range(rows)],
            "high": [101.0 + i for i in range(rows)],
            "low": [99.0 + i for i in range(rows)],
            "close": [100.5 + i for i in range(rows)],
            "volume": [1000 + i for i in range(rows)],
        }
    )


def test_ohlc_inconsistency_is_rejected() -> None:
    frame = _ohlcv(2)
    frame.loc[0, "high"] = 50.0
    with pytest.raises(MarketDataValidationError, match="high must be"):
        validate_ohlcv(frame)


def test_non_positive_prices_are_rejected() -> None:
    frame = _ohlcv(2)
    frame.loc[0, "close"] = 0.0
    with pytest.raises(MarketDataValidationError, match="positive"):
        validate_ohlcv(frame)


def test_normalize_preserves_adj_close() -> None:
    source = pd.DataFrame(
        {
            "Date": ["2020-01-01", "2020-01-02"],
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Adj Close": [100.5, 101.5],
            "Volume": [1000, 1100],
        }
    )
    result = normalize_ohlcv(source)
    assert "adj_close" in result.columns
    assert result["adj_close"].tolist() == [100.5, 101.5]


def test_fingerprint_is_deterministic() -> None:
    frame = _ohlcv(4)
    a = fingerprint_ohlcv(frame, symbol="AAPL", provider="yahoo")
    b = fingerprint_ohlcv(frame, symbol="AAPL", provider="yahoo")
    assert a == b
    assert len(a) == 32
    spec = build_dataset_spec(frame, symbol="AAPL", provider="yahoo")
    assert spec.dataset_id.startswith("yahoo:AAPL:")
    assert a in spec.dataset_id


def test_instrument_classification() -> None:
    assert classify_instrument("^GSPC") == "index"
    assert classify_instrument("BTC-USD") == "crypto"
    assert classify_instrument("SPY") == "etf"
    assert InstrumentRef.from_symbol("brk-b").symbol == "BRK-B"


def test_quality_report_flags_large_gaps() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-02-01"]),
            "open": [1.0, 1.0, 1.0],
            "high": [1.1, 1.1, 1.1],
            "low": [0.9, 0.9, 0.9],
            "close": [1.0, 1.0, 1.0],
            "volume": [10, 10, 10],
        }
    )
    report = assess_market_data_quality(frame, large_gap_days=10)
    assert report.max_gap_days >= 10
    assert report.large_gap_dates
    assert any("gap" in warning for warning in report.warnings)


def test_chronological_split_purge_removes_leaky_tails() -> None:
    rows = 100
    dates = pd.Series(pd.date_range("2020-01-01", periods=rows))
    frame = SupervisedFrame(
        X=pd.DataFrame({"feature": range(rows)}),
        y=pd.Series(range(rows), name="target"),
        dates=dates,
        feature_names=("feature",),
    )
    unpurged = chronological_split(frame)
    purged = chronological_split(frame, forecast_horizon=5)
    assert len(purged.train.X) == len(unpurged.train.X) - 5
    assert len(purged.validation.X) == len(unpurged.validation.X) - 5
    # Last train index + horizon must not reach validation start index.
    train_last = purged.train.X.index[-1] if False else len(purged.train.X) - 1
    assert train_last + 5 < 70  # validation starts at row 70 for 100*0.7


def test_feature_set_identity_stable() -> None:
    params = {"return_lags": (1, 2), "rsi_period": 14}
    assert feature_parameters_id(params) == feature_parameters_id(dict(params))
    spec = build_feature_set_spec(("r1", "rsi_14"), parameters=params, lookback_bars=14)
    assert spec.feature_set_id.startswith("fs:")
