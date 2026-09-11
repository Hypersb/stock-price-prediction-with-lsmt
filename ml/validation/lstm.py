"""Walk-forward evaluation of independently trained LSTM models."""

import pandas as pd
import torch

from ml.neural.alignment import create_dated_sequences
from ml.neural.dataset import FinancialSequenceDataset
from ml.neural.loaders import create_sequence_loader
from ml.neural.lstm import LSTMClassifier, LSTMRegressor
from ml.training.config import TrainingConfig
from ml.training.evaluation import evaluate_lstm
from ml.training.trainer import train_lstm
from ml.validation.baselines import WalkForwardModelResult
from ml.validation.config import WalkForwardConfig
from ml.validation.folds import WalkForwardFold
from ml.validation.preprocessing import preprocess_fold
from ml.validation.purging import purge_fold


def evaluate_lstm_walk_forward(
    X: pd.DataFrame,
    y: pd.Series,
    dates: pd.Series | pd.Index,
    folds: list[WalkForwardFold],
    *,
    task: str,
    config: WalkForwardConfig,
    lookback: int = 20,
    training_config: TrainingConfig | None = None,
    hidden_size: int = 16,
) -> list[WalkForwardModelResult]:
    """Train a fresh LSTM independently for every purged walk-forward fold."""
    if task not in {"regression", "classification"}:
        raise ValueError("task must be 'regression' or 'classification'")
    parsed_dates = pd.DatetimeIndex(pd.to_datetime(dates))
    results: list[WalkForwardModelResult] = []
    for fold in folds:
        safe_fold = purge_fold(fold, config)
        transformed = preprocess_fold(
            X.iloc[safe_fold.train_indices],
            X.iloc[safe_fold.validation_indices],
            X.iloc[safe_fold.test_indices],
        )
        train_dates = parsed_dates[safe_fold.train_indices]
        validation_dates = parsed_dates[safe_fold.validation_indices]
        test_dates = parsed_dates[safe_fold.test_indices]
        train_sequences = create_dated_sequences(
            transformed.X_train.to_numpy(),
            y.iloc[safe_fold.train_indices].to_numpy(),
            train_dates,
            lookback,
        )
        validation_sequences = create_dated_sequences(
            transformed.X_validation.to_numpy(),
            y.iloc[safe_fold.validation_indices].to_numpy(),
            validation_dates,
            lookback,
        )
        test_sequences = create_dated_sequences(
            transformed.X_test.to_numpy(),
            y.iloc[safe_fold.test_indices].to_numpy(),
            test_dates,
            lookback,
        )
        train_loader = create_sequence_loader(FinancialSequenceDataset(*train_sequences), 32)
        validation_loader = create_sequence_loader(
            FinancialSequenceDataset(*validation_sequences), 32
        )
        test_loader = create_sequence_loader(FinancialSequenceDataset(*test_sequences), 32)
        model_type = LSTMRegressor if task == "regression" else LSTMClassifier
        model = model_type(input_size=X.shape[1], hidden_size=hidden_size)
        result = train_lstm(
            model,
            train_loader,
            validation_loader,
            task=task,
            configuration=training_config or TrainingConfig(epochs=2, patience=1, device="cpu"),
            metadata={"fold": safe_fold.fold, "lookback": lookback},
        )
        evaluation = evaluate_lstm(result.model, test_loader, task=task, split="test")
        predicted, probabilities = _predict_with_probabilities(
            result.model,
            test_loader,
            task,
            result.configuration.torch_device(),
        )
        results.append(
            WalkForwardModelResult(
                safe_fold.fold,
                "lstm",
                task,
                evaluation.metrics,
                test_sequences[2],
                test_sequences[1],
                predicted,
                probabilities,
            )
        )
    return results


def _predict_with_probabilities(model, loader, task, device):
    """Return class/value predictions and classification probabilities when available."""
    from ml.training.epochs import validate_epoch
    from ml.training.optimization import create_loss

    _, predictions, _ = validate_epoch(model, loader, create_loss(task), device)
    logits = predictions.detach().cpu()
    if task == "classification":
        probabilities = torch.sigmoid(logits).numpy()
        classes = (probabilities >= 0.5).astype(int)
        return classes, probabilities
    return logits.numpy(), None
