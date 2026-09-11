"""Tests for backtest sensitivity analysis."""

import numpy as np
import pandas as pd

from ml.backtesting.config import BacktestConfig
from ml.research.sensitivity import (
    net_return_for_fixed_positions,
    run_backtest_sensitivity,
)


def test_higher_costs_cannot_increase_net_return_for_identical_positions() -> None:
    positions = pd.Series([0.0, 1.0, 1.0, 0.0, -1.0, 0.0])
    realized = pd.Series([0.01, 0.02, -0.01, 0.015, 0.01, -0.005])
    returns = [
        net_return_for_fixed_positions(positions, realized, transaction_cost_bps=cost)
        for cost in (0.0, 5.0, 10.0, 25.0)
    ]
    assert returns == sorted(returns, reverse=True)
    assert returns[0] > returns[-1]


def test_sensitivity_table_covers_cost_scenarios() -> None:
    dates = pd.date_range("2020-01-01", periods=12, freq="D")
    predictions = pd.DataFrame(
        {
            "date": dates,
            "fold": 0,
            "model": ["linear_regression"] * 12,
            "task": ["regression"] * 12,
            "actual": np.linspace(-0.01, 0.01, 12),
            "predicted": np.linspace(-0.008, 0.012, 12),
        }
    )
    market = pd.DataFrame(
        {
            "date": dates,
            "realized_return": np.linspace(-0.01, 0.01, 12),
        }
    )
    result = run_backtest_sensitivity(
        predictions,
        market,
        base_config=BacktestConfig(strategy_mode="long_only", signal_threshold=0.0),
        cost_scenarios_bps=(0.0, 5.0, 10.0, 25.0),
        signal_thresholds=(0.0, 0.005),
    )
    table = result.to_frame()
    assert len(table) == 8
    assert set(table["transaction_cost_bps"]) == {0.0, 5.0, 10.0, 25.0}
    zero = table[table["transaction_cost_bps"] == 0.0]["net_return"].mean()
    high = table[table["transaction_cost_bps"] == 25.0]["net_return"].mean()
    assert zero >= high
    assert any("diagnostic" in note for note in result.notes)
