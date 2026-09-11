"""Tests for the final research evaluation pipeline."""

import numpy as np
import pandas as pd

from ml.research.config import tiny_fixture_config
from ml.research.pipeline import run_final_research_evaluation


def _ohlcv(rows: int = 100, seed: int = 0, drift: float = 0.001) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    close = 100 * np.cumprod(1 + drift + rng.normal(0.0, 0.01, size=rows))
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


def test_final_pipeline_runs_on_tiny_deterministic_fixtures() -> None:
    config = tiny_fixture_config(("SYN_A", "SYN_B"))
    market_data = {
        "SYN_A": _ohlcv(rows=110, seed=1, drift=0.002),
        "SYN_B": _ohlcv(rows=110, seed=2, drift=-0.001),
    }

    result = run_final_research_evaluation(market_data, config)

    assert result.experiment_id == config.fingerprint()
    assert len(result.multi_asset.assets) == 2
    assert result.ablation_results
    assert result.complexity is not None
    assert result.statistical_comparisons
    assert any("fingerprint" in note for note in result.notes)


def test_configuration_fingerprint_is_stable() -> None:
    first = tiny_fixture_config().fingerprint()
    second = tiny_fixture_config().fingerprint()
    assert first == second
    assert len(first) == 16
