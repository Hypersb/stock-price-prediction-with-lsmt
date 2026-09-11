import numpy as np
import pandas as pd
import pytest

from ml.backtesting.config import BacktestConfig
from ml.backtesting.execution import align_execution
from ml.backtesting.signals import prediction_signals
from ml.training.config import TrainingConfig
from ml.validation.config import WalkForwardConfig
from ml.validation.folds import generate_expanding_folds
from ml.validation.lstm import evaluate_lstm_walk_forward
from ml.validation.predictions import collect_predictions


def test_lstm_walk_forward_runs_tiny_regression_fold() -> None:
    X = pd.DataFrame({"feature": np.linspace(0.0, 1.0, 30)})
    y = pd.Series(np.linspace(-0.1, 0.1, 30))
    dates = pd.date_range("2020-01-01", periods=30)
    config = WalkForwardConfig(initial_train_size=12, validation_size=6, test_size=6, step_size=6)

    results = evaluate_lstm_walk_forward(
        X,
        y,
        dates,
        generate_expanding_folds(30, config),
        task="regression",
        config=config,
        lookback=3,
        hidden_size=4,
        training_config=TrainingConfig(epochs=1, patience=1, device="cpu"),
    )

    assert len(results) == 2
    assert results[0].model_name == "lstm"
    # With train+validation context, all test_size targets are recoverable.
    assert len(results[0].dates) == 6
    assert results[0].dates[0] == pd.Timestamp("2020-01-19")
    assert results[0].dates[-1] == pd.Timestamp("2020-01-24")


def test_lstm_test_sequences_use_prior_partition_feature_context() -> None:
    """Boundary: first test target may legally use train/val features only."""
    from ml.neural.alignment import create_dated_sequences_with_context
    from ml.validation.preprocessing import preprocess_fold

    X = pd.DataFrame({"feature": np.linspace(0.0, 1.0, 24)})
    y = pd.Series(np.linspace(-0.1, 0.1, 24))
    dates = pd.date_range("2020-01-01", periods=24)
    train_idx = list(range(0, 12))
    val_idx = list(range(12, 18))
    test_idx = list(range(18, 24))
    transformed = preprocess_fold(X.iloc[train_idx], X.iloc[val_idx], X.iloc[test_idx])
    context = np.concatenate(
        [transformed.X_train.to_numpy(), transformed.X_validation.to_numpy()], axis=0
    )
    sequences, targets, target_dates = create_dated_sequences_with_context(
        context,
        transformed.X_test.to_numpy(),
        y.iloc[test_idx].to_numpy(),
        dates[test_idx],
        lookback=3,
    )
    assert len(targets) == 6
    assert target_dates[0] == dates[18]
    # Sequence ending at first test row uses last two context rows + first test row.
    assert sequences[0].shape == (3, 1)
    np.testing.assert_allclose(
        sequences[0][-1, 0],
        float(transformed.X_test.to_numpy()[0, 0]),
    )
    np.testing.assert_allclose(
        sequences[0][0, 0],
        float(context[-2, 0]),
    )


def test_lstm_classification_oos_includes_probabilities() -> None:
    rng = np.random.default_rng(0)
    X = pd.DataFrame({"feature": rng.normal(size=40)})
    y = pd.Series((X["feature"] > 0).astype(int))
    dates = pd.date_range("2020-01-01", periods=40)
    config = WalkForwardConfig(initial_train_size=16, validation_size=8, test_size=8, step_size=8)

    results = evaluate_lstm_walk_forward(
        X,
        y,
        dates,
        generate_expanding_folds(40, config),
        task="classification",
        config=config,
        lookback=3,
        hidden_size=4,
        training_config=TrainingConfig(epochs=1, patience=1, device="cpu", seed=1),
    )
    assert results
    assert results[0].probabilities is not None
    assert len(results[0].probabilities) == len(results[0].predicted)
    frame = collect_predictions(results)
    assert "probability" in frame.columns
    signals = prediction_signals(frame[frame["model"] == "lstm"], BacktestConfig())
    assert "signal" in signals.columns


def test_backtest_execution_rejects_horizon_greater_than_one() -> None:
    signals = pd.DataFrame({"date": pd.to_datetime(["2020-01-01"]), "signal": [1]})
    market = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "realized_return": [0.0, 0.1],
        }
    )
    with pytest.raises(ValueError, match="forecast_horizon=1"):
        align_execution(signals, market, forecast_horizon=2)
