"""Validation-loss early stopping with safe best-state snapshots."""

from copy import deepcopy

import torch


class EarlyStopping:
    """Track validation improvement and restore the best model state."""

    def __init__(self, patience: int = 5, min_delta: float = 0.0) -> None:
        if patience <= 0 or min_delta < 0:
            raise ValueError("patience must be positive and min_delta nonnegative")
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float("inf")
        self.best_epoch: int | None = None
        self.wait = 0
        self.best_state: dict[str, torch.Tensor] | None = None

    def update(self, validation_loss: float, epoch: int, model: torch.nn.Module) -> bool:
        """Record validation loss and return whether training should stop."""
        if validation_loss < self.best_loss - self.min_delta:
            self.best_loss = validation_loss
            self.best_epoch = epoch
            self.wait = 0
            self.best_state = deepcopy(model.state_dict())
            return False
        self.wait += 1
        return self.wait >= self.patience

    def restore(self, model: torch.nn.Module) -> None:
        """Restore the immutable best validation state."""
        if self.best_state is None:
            raise RuntimeError("no best model state is available")
        model.load_state_dict(self.best_state)