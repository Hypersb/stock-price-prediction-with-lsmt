"""Tests for feature-group ablation studies."""

import numpy as np
import pandas as pd
import pytest

from ml.research.ablation import (
    FEATURE_GROUPS,
    exclude_feature_groups,
    feature_names_for_groups,
    run_feature_ablation_study,
)


def _ohlcv(rows: int = 160, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    close = 100 * np.cumprod(1 + rng.normal(0.001, 0.01, size=rows))
    return pd.DataFrame(
        {
            "date": dates,
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": rng.integers(1000, 5000, size=rows),
        }
    )


_FEATURE_PARAMETERS = {
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


def test_feature_group_selection_and_exclusion() -> None:
    names = (
        "simple_return",
        "return_lag_1",
        "momentum_5",
        "sma_5",
        "volatility_5",
        "volume_change",
        "rsi_5",
        "macd",
    )
    returns = feature_names_for_groups(names, ("returns",))
    assert returns == ("simple_return", "return_lag_1")
    without_returns = exclude_feature_groups(names, ("returns",))
    assert "simple_return" not in without_returns
    assert "momentum_5" in without_returns


def test_ablation_study_returns_aligned_comparisons() -> None:
    results = run_feature_ablation_study(
        _ohlcv(),
        feature_parameters=_FEATURE_PARAMETERS,
        excluded_group_experiments=("returns", "momentum", "volatility"),
        include_single_group_only=True,
    )
    experiments = {result.experiment for result in results}
    assert "all_minus_returns" in experiments
    assert "only_momentum" in experiments
    for result in results:
        assert result.observations > 0
        assert set(result.baseline_metrics) == set(result.ablated_metrics)
        assert set(result.absolute_change) == set(result.baseline_metrics)
        assert any("not automatically meaningful" in note for note in result.notes)


def test_unknown_feature_group_rejected() -> None:
    with pytest.raises(ValueError, match="unknown feature groups"):
        feature_names_for_groups(("sma_5",), ("not_a_group",))


def test_feature_groups_cover_documented_categories() -> None:
    assert set(FEATURE_GROUPS) >= {
        "returns",
        "momentum",
        "trend",
        "volatility",
        "volume",
        "technical",
    }
