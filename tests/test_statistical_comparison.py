"""Deterministic tests for block-bootstrap model comparison."""

import numpy as np
import pandas as pd
import pytest

from ml.research.statistics import compare_models_block_bootstrap


def _paired_predictions(seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2020-01-01", periods=80, freq="D")
    actual = rng.normal(0.0, 0.02, size=80)
    # Model A is systematically closer than model B.
    pred_a = actual + rng.normal(0.0, 0.005, size=80)
    pred_b = actual + rng.normal(0.0, 0.03, size=80)
    rows = []
    for date, y, a, b in zip(dates, actual, pred_a, pred_b, strict=True):
        rows.append({"date": date, "model": "model_a", "actual": y, "predicted": a})
        rows.append({"date": date, "model": "model_b", "actual": y, "predicted": b})
    return pd.DataFrame(rows)


def test_block_bootstrap_comparison_is_deterministic_with_fixed_seed() -> None:
    predictions = _paired_predictions()
    first = compare_models_block_bootstrap(
        predictions,
        model_a="model_a",
        model_b="model_b",
        metric="mae",
        block_length=4,
        bootstrap_iterations=200,
        seed=123,
    )
    second = compare_models_block_bootstrap(
        predictions,
        model_a="model_a",
        model_b="model_b",
        metric="mae",
        block_length=4,
        bootstrap_iterations=200,
        seed=123,
    )
    assert first.observed_difference == second.observed_difference
    assert first.confidence_interval == second.confidence_interval
    assert first.method == "moving_block_bootstrap"
    assert first.observations == 80
    assert first.observed_difference < 0
    assert any("not prove" in note for note in first.notes)


def test_block_bootstrap_requires_aligned_actuals() -> None:
    frame = _paired_predictions()
    frame.loc[frame["model"] == "model_b", "actual"] = 999.0
    with pytest.raises(ValueError, match="paired actuals"):
        compare_models_block_bootstrap(
            frame,
            model_a="model_a",
            model_b="model_b",
            bootstrap_iterations=50,
            seed=1,
        )
