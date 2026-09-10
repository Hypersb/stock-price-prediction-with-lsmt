"""Neural architecture configuration and device selection."""

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class NeuralConfig:
    """Validated configuration shared by sequence and model experiments."""

    lookback: int = 20
    input_size: int = 1
    hidden_size: int = 64
    num_layers: int = 1
    dropout: float = 0.0
    batch_size: int = 32
    seed: int = 42

    def __post_init__(self) -> None:
        for name in ("lookback", "input_size", "hidden_size", "num_layers", "batch_size"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in the range [0, 1)")
        if isinstance(self.seed, bool) or not isinstance(self.seed, int):
            raise TypeError("seed must be an integer")


def resolve_device(prefer_accelerator: bool = True) -> torch.device:
    """Return CUDA, MPS, or CPU according to availability and preference."""
    if prefer_accelerator and torch.cuda.is_available():
        return torch.device("cuda")
    mps = getattr(torch.backends, "mps", None)
    if prefer_accelerator and mps is not None and mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")