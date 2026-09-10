"""Loss and optimizer factories for supported LSTM tasks."""

from collections.abc import Iterable

import torch
from torch import nn


def create_loss(task: str) -> nn.Module:
    """Create MSE loss for regression or logits-aware BCE loss for direction."""
    if task == "regression":
        return nn.MSELoss()
    if task == "classification":
        return nn.BCEWithLogitsLoss()
    raise ValueError("task must be 'regression' or 'classification'")


def create_optimizer(
    parameters: Iterable[torch.nn.Parameter],
    learning_rate: float = 1e-3,
    weight_decay: float = 0.0,
) -> torch.optim.Optimizer:
    """Create Adam using only the supplied model parameters."""
    if learning_rate <= 0 or weight_decay < 0:
        raise ValueError("learning_rate must be positive and weight_decay nonnegative")
    return torch.optim.Adam(parameters, lr=learning_rate, weight_decay=weight_decay)