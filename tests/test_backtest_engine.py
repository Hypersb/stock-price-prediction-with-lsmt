import pandas as pd

from ml.backtesting.config import BacktestConfig
from ml.backtesting.engine import run_backtest


def test_backtest_engine_runs_out_of_sample_prediction_flow() -> None:
    dates = pd.date_range("2020-01-01", periods=4)
    predictions = pd.DataFrame({"date": dates[:3], "model": "oos_model", "task": "regression", "predicted": [0.1, -0.1, 0.1]})
    returns = pd.DataFrame({"date": dates, "realized_return": [0.5, 0.1, -0.1, 0.1]})

    result = run_backtest(predictions, returns, BacktestConfig(transaction_cost_bps=10))

    assert result.observations == 3
    assert result.timeline["realization_date"].tolist() == list(dates[1:])
    assert "sharpe_ratio" in result.metrics
    assert "buy_and_hold" in result.benchmark