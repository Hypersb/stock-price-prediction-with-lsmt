import numpy as np

from ml.neural.dataset import FinancialSequenceDataset
from ml.neural.loaders import create_sequence_loader
from ml.neural.lstm import LSTMRegressor
from ml.training.config import TrainingConfig
from ml.training.trainer import train_lstm


def test_trainer_runs_regression_without_test_loader() -> None:
    dataset = FinancialSequenceDataset(np.ones((6, 3, 2)), np.ones(6))
    loader = create_sequence_loader(dataset, 2)
    model = LSTMRegressor(input_size=2, hidden_size=4)

    result = train_lstm(
        model,
        loader,
        loader,
        task="regression",
        configuration=TrainingConfig(epochs=3, patience=2, device="cpu"),
        metadata={"lookback": 3},
    )

    assert result.best_epoch >= 1
    assert len(result.history.records) <= 3
    assert result.metadata["task"] == "regression"