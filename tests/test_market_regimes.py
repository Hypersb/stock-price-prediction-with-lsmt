"""Tests for causal market regime labeling and evaluation."""

import numpy as np
import pandas as pd
import pytest

from ml.research.regimes import (
    RegimeConfig,
    evaluate_metrics_by_regime,
    label_market_regimes,
)


def _ohlcv(rows: int = 200, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2018-01-01", periods=rows, freq="D")
    # Strong early uptrend then downtrend so both regimes appear.
    drift = np.concatenate(
        [
            np.full(rows // 2, 0.003),
            np.full(rows - rows // 2, -0.003),
        ]
    )
    noise = rng.normal(0.0, 0.01, size=rows)
    close = 100 * np.cumprod(1 + drift + noise)
    return pd.DataFrame(
        {
            "date": dates,
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": rng.integers(1_000, 5_000, size=rows),
        }
    )


def test_future_observations_do_not_alter_historical_regime_labels() -> None:
    full = _ohlcv(rows=220, seed=1)
    prefix = full.iloc[:180].copy()
    config = RegimeConfig(
        trend_ma_window=20,
        trend_return_window=10,
        volatility_window=10,
        volatility_min_history=40,
        min_observations_per_regime=5,
    )

    prefix_labels = label_market_regimes(prefix, config).labels
    full_labels = label_market_regimes(full, config).labels

    compared = [
        "trend_regime",
        "volatility_regime",
        "trailing_ma",
        "trailing_return",
        "realized_volatility",
        "vol_low_threshold",
        "vol_high_threshold",
    ]
    for column in compared:
        left = prefix_labels[column].to_numpy()
        right = full_labels[column].iloc[:180].to_numpy()
        if column.endswith("regime"):
            assert np.array_equal(left, right) or (
                pd.isna(left) == pd.isna(right)
            ).all() and np.array_equal(
                left[~pd.isna(left)], right[~pd.isna(right)]
            )
        else:
            np.testing.assert_allclose(
                left.astype(float),
                right.astype(float),
                equal_nan=True,
                rtol=0,
                atol=0,
            )


def test_regime_labels_only_use_documented_dimensions() -> None:
    labels = label_market_regimes(
        _ohlcv(),
        RegimeConfig(
            trend_ma_window=20,
            trend_return_window=10,
            volatility_window=10,
            volatility_min_history=40,
        ),
    ).labels
    assert set(labels["trend_regime"].dropna().unique()).issubset({"bullish", "bearish", "neutral"})
    assert set(labels["volatility_regime"].dropna().unique()).issubset({"low", "normal", "high"})


def test_regime_metric_evaluation_respects_minimum_counts() -> None:
    regimes = label_market_regimes(
        _ohlcv(rows=180, seed=2),
        RegimeConfig(
            trend_ma_window=15,
            trend_return_window=8,
            volatility_window=8,
            volatility_min_history=30,
            min_observations_per_regime=50,
        ),
    ).labels
    predictions = pd.DataFrame(
        {
            "date": regimes["date"].iloc[60:100],
            "model": ["linear_regression"] * 40,
            "actual": np.linspace(-0.01, 0.01, 40),
            "predicted": np.linspace(-0.008, 0.012, 40),
        }
    )
    results = evaluate_metrics_by_regime(predictions, regimes, config=RegimeConfig(min_observations_per_regime=50))
    assert results
    assert all(not result.interpretable for result in results)
    assert all("insufficient observations" in result.note for result in results)


def test_regime_config_rejects_invalid_quantiles() -> None:
    with pytest.raises(ValueError, match="quantiles"):
        RegimeConfig(volatility_low_quantile=0.8, volatility_high_quantile=0.2)
