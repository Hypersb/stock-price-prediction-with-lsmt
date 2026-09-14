"""Deterministic tests for multi-asset robustness evaluation."""

import numpy as np
import pandas as pd
import pytest

from ml.research.dataset_prep import prepare_research_frame
from ml.research.multi_asset import (
    evaluate_multi_asset_robustness,
    evaluate_single_asset_robustness,
)
from ml.research.universe import DEFAULT_RESEARCH_UNIVERSE, ResearchUniverse
from ml.training.config import TrainingConfig
from ml.validation.config import WalkForwardConfig


def _synthetic_ohlcv(rows: int = 120, seed: int = 0, drift: float = 0.001) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    noise = rng.normal(0.0, 0.01, size=rows)
    close = 100 * np.cumprod(1 + drift + noise)
    open_ = close * (1 + rng.normal(0.0, 0.002, size=rows))
    body_high = np.maximum(open_, close)
    body_low = np.minimum(open_, close)
    high = body_high * (1 + rng.uniform(0.0, 0.01, size=rows))
    low = body_low * (1 - rng.uniform(0.0, 0.01, size=rows))
    volume = rng.integers(100_000, 500_000, size=rows)
    return pd.DataFrame(
        {
            "date": dates,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


def test_default_research_universe_is_diversified_example() -> None:
    assert DEFAULT_RESEARCH_UNIVERSE == ("AAPL", "MSFT", "JPM", "XOM", "SPY")
    universe = ResearchUniverse()
    assert universe.symbols == DEFAULT_RESEARCH_UNIVERSE


def test_research_universe_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="unique"):
        ResearchUniverse(symbols=("AAPL", "aapl"))


def test_multi_asset_evaluation_preserves_per_symbol_results() -> None:
    data = {
        "AAA": _synthetic_ohlcv(rows=130, seed=1, drift=0.002),
        "BBB": _synthetic_ohlcv(rows=130, seed=2, drift=-0.001),
    }
    feature_parameters = {
        "return_lags": (1, 2),
        "momentum_windows": (5,),
        "moving_average_windows": (5, 10),
        "ema_spans": (5,),
        "volatility_windows": (5,),
        "volume_window": 5,
        "rsi_period": 5,
        "macd_fast": 3,
        "macd_slow": 6,
        "macd_signal": 2,
        "atr_period": 5,
    }
    walk_forward = WalkForwardConfig(
        initial_train_size=40,
        validation_size=10,
        test_size=10,
        step_size=20,
        forecast_horizon=1,
    )

    result = evaluate_multi_asset_robustness(
        data,
        universe=ResearchUniverse(symbols=("AAA", "BBB", "MISSING")),
        target_type="regression",
        horizon=1,
        feature_parameters=feature_parameters,
        walk_forward=walk_forward,
        model_families=("naive", "linear"),
        include_lstm=False,
    )

    assert result.universe == ("AAA", "BBB", "MISSING")
    assert {asset.symbol for asset in result.assets} == {"AAA", "BBB"}
    assert result.skipped_symbols[0][0] == "MISSING"
    table = result.summary_table()
    assert set(table["symbol"]) == {"AAA", "BBB"}
    assert "naive_regression" in set(table["model"])
    assert "linear_regression" in set(table["model"])
    # No blended cross-asset row that could hide a weak symbol.
    assert "ALL" not in set(table["symbol"])
    assert len(table) == 4


def test_single_asset_can_include_lstm_on_tiny_fixture() -> None:
    frame = prepare_research_frame(
        _synthetic_ohlcv(rows=90, seed=3),
        symbol="SYN",
        target_type="regression",
        horizon=1,
        feature_parameters={
            "return_lags": (1,),
            "momentum_windows": (3,),
            "moving_average_windows": (3,),
            "ema_spans": (3,),
            "volatility_windows": (3,),
            "volume_window": 3,
            "rsi_period": 3,
            "macd_fast": 2,
            "macd_slow": 4,
            "macd_signal": 2,
            "atr_period": 3,
        },
    )
    walk_forward = WalkForwardConfig(
        initial_train_size=30,
        validation_size=8,
        test_size=8,
        step_size=20,
        forecast_horizon=1,
    )

    result = evaluate_single_asset_robustness(
        frame,
        walk_forward=walk_forward,
        model_families=("naive", "lstm"),
        lookback=3,
        hidden_size=4,
        training_config=TrainingConfig(epochs=1, patience=1, device="cpu", seed=7),
    )

    names = {summary.model_name for summary in result.model_summaries}
    assert names == {"naive_regression", "lstm"}
    assert result.symbol == "SYN"
    assert not result.predictions.empty
    assert set(result.predictions["model"]) == names


def test_prepare_research_frame_uses_same_horizon_target() -> None:
    frame = prepare_research_frame(
        _synthetic_ohlcv(rows=80, seed=4),
        symbol="syn",
        target_type="direction",
        horizon=2,
        feature_parameters={
            "return_lags": (1,),
            "momentum_windows": (3,),
            "moving_average_windows": (3,),
            "ema_spans": (3,),
            "volatility_windows": (3,),
            "volume_window": 3,
            "rsi_period": 3,
            "macd_fast": 2,
            "macd_slow": 4,
            "macd_signal": 2,
            "atr_period": 3,
        },
    )
    assert frame.symbol == "SYN"
    assert frame.task == "classification"
    assert frame.target_column == "direction_2"
    assert frame.horizon == 2
    assert len(frame.feature_names) > 0
