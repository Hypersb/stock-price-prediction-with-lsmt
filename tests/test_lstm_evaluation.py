import numpy as np

from ml.neural.dataset import FinancialSequenceDataset
from ml.neural.loaders import create_sequence_loader
from ml.neural.lstm import LSTMClassifier, LSTMRegressor
from ml.training.evaluation import evaluate_lstm


def test_lstm_regression_evaluation_uses_existing_metrics() -> None:
    dataset = FinancialSequenceDataset(np.ones((4, 2, 1)), np.array([0.0, 0.1, 0.0, -0.1]))
    result = evaluate_lstm(
        LSTMRegressor(input_size=1, hidden_size=3),
        create_sequence_loader(dataset, 2),
        task="regression",
    )

    assert result.dataset_split == "validation"
    assert {"mae", "rmse", "directional_accuracy"}.issubset(result.metrics)


def test_lstm_classification_evaluation_converts_logits_to_probabilities() -> None:
    dataset = FinancialSequenceDataset(np.ones((4, 2, 1)), np.array([0, 1, 0, 1]))
    result = evaluate_lstm(
        LSTMClassifier(input_size=1, hidden_size=3),
        create_sequence_loader(dataset, 2),
        task="classification",
    )

    assert "accuracy" in result.metrics
    assert 0.0 <= result.metrics["accuracy"] <= 1.0