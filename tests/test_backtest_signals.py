import pandas as pd
import pytest

from ml.backtesting.config import BacktestConfig
from ml.backtesting.signals import prediction_signals


def test_regression_signals_support_long_only_and_long_short() -> None:
    predictions = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=3), "model": "m", "task": "regression", "predicted": [0.1, -0.1, 0.0]})

    long_only = prediction_signals(predictions, BacktestConfig(signal_threshold=0.05))
    long_short = prediction_signals(predictions, BacktestConfig(strategy_mode="long_short", signal_threshold=0.05))

    assert long_only["signal"].tolist() == [1, 0, 0]
    assert long_short["signal"].tolist() == [1, -1, 0]


def test_classification_probability_is_validated() -> None:
    predictions = pd.DataFrame({"date": [pd.Timestamp("2020-01-01")], "model": "m", "task": "classification", "probability": [1.2]})

    with pytest.raises(ValueError, match="probabilities"):
        prediction_signals(predictions, BacktestConfig())