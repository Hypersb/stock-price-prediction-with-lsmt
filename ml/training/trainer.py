"""Complete train/validation orchestration for LSTM experiments."""

from dataclasses import dataclass
from typing import Any

import torch
from torch.utils.data import DataLoader

from ml.neural.reproducibility import set_random_seed
from ml.training.config import TrainingConfig
from ml.training.early_stopping import EarlyStopping
from ml.training.epochs import train_epoch, validate_epoch
from ml.training.history import TrainingHistory
from ml.training.optimization import create_loss, create_optimizer


@dataclass(frozen=True)
class TrainingResult:
    """Model and metadata produced by train/validation-only fitting."""

    model: torch.nn.Module
    best_epoch: int
    best_validation_loss: float
    history: TrainingHistory
    stopped_early: bool
    configuration: TrainingConfig
    metadata: dict[str, Any]


def train_lstm(
    model: torch.nn.Module,
    train_loader: DataLoader,
    validation_loader: DataLoader,
    *,
    task: str,
    configuration: TrainingConfig | None = None,
    metadata: dict[str, Any] | None = None,
) -> TrainingResult:
    """Train on train data and use validation loss for stopping/restoration only."""
    config = configuration or TrainingConfig()
    set_random_seed(config.seed)
    device = config.torch_device()
    model.to(device)
    criterion = create_loss(task)
    optimizer = create_optimizer(model.parameters(), config.learning_rate, config.weight_decay)
    stopping = EarlyStopping(config.patience, config.min_delta)
    history = TrainingHistory()
    stopped_early = False
    for epoch in range(1, config.epochs + 1):
        training_loss = train_epoch(
            model, train_loader, optimizer, criterion, device, config.gradient_clip_norm
        )
        validation_loss, _, _ = validate_epoch(model, validation_loader, criterion, device)
        history.append(epoch, training_loss, validation_loss)
        if stopping.update(validation_loss, epoch, model):
            stopped_early = True
            break
    stopping.restore(model)
    return TrainingResult(
        model=model,
        best_epoch=stopping.best_epoch or 0,
        best_validation_loss=stopping.best_loss,
        history=history,
        stopped_early=stopped_early,
        configuration=config,
        metadata={"task": task, **(metadata or {})},
    )