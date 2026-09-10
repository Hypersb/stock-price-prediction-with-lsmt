"""Configuration for LSTM training experiments."""

from dataclasses import dataclass

import torch

from ml.neural.config import resolve_device


@dataclass(frozen=True)
class TrainingConfig:
    """Validated optimization and early-stopping settings."""

    epochs: int = 50
    learning_rate: float = 1e-3
    weight_decay: float = 0.0
    patience: int = 5
    min_delta: float = 0.0
    gradient_clip_norm: float | None = 1.0
    seed: int = 42
    device: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.epochs, bool) or not isinstance(self.epochs, int) or self.epochs <= 0:
            raise ValueError("epochs must be a positive integer")
        if self.learning_rate <= 0 or self.weight_decay < 0:
            raise ValueError("learning_rate must be positive and weight_decay nonnegative")
        if isinstance(self.patience, bool) or not isinstance(self.patience, int) or self.patience <= 0:
            raise ValueError("patience must be a positive integer")
        if self.min_delta < 0:
            raise ValueError("min_delta must be nonnegative")
        if self.gradient_clip_norm is not None and self.gradient_clip_norm <= 0:
            raise ValueError("gradient_clip_norm must be positive when enabled")
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer")

    def torch_device(self) -> torch.device:
        """Resolve the configured device, defaulting to the available device."""
        return torch.device(self.device) if self.device else resolve_device()