"""Evaluation adapters for trained LSTM models."""

from dataclasses import dataclass

import numpy as np
import torch
from torch.utils.data import DataLoader

from ml.evaluation.classification import evaluate_classification
from ml.evaluation.regression import evaluate_regression
from ml.training.epochs import validate_epoch
from ml.training.optimization import create_loss


@dataclass(frozen=True)
class LSTMEvaluation:
    """Named task, split, loss, and predictive metrics."""

    model_name: str
    task: str
    dataset_split: str
    loss: float
    metrics: dict[str, object]


def evaluate_lstm(
    model: torch.nn.Module,
    loader: DataLoader,
    *,
    task: str,
    split: str = "validation",
    device: torch.device | None = None,
    model_name: str = "lstm",
) -> LSTMEvaluation:
    """Evaluate a trained LSTM and adapt outputs to existing metric functions."""
    resolved_device = device or torch.device("cpu")
    loss, predictions, targets = validate_epoch(model, loader, create_loss(task), resolved_device)
    if task == "regression":
        metrics = evaluate_regression(targets.numpy(), predictions.numpy())
    elif task == "classification":
        probabilities = torch.sigmoid(predictions).numpy()
        labels = (probabilities >= 0.5).astype(int)
        metrics = evaluate_classification(targets.numpy(), labels, probabilities)
    else:
        raise ValueError("task must be 'regression' or 'classification'")
    return LSTMEvaluation(model_name, task, split, loss, metrics)