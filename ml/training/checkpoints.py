"""Safe state-dictionary checkpoint utilities."""

from pathlib import Path
from typing import Any

import torch


def save_checkpoint(
    path: Path | str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    validation_loss: float,
    metadata: dict[str, Any],
) -> Path:
    """Save model/optimizer state and structured experiment metadata."""
    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": epoch,
            "validation_loss": validation_loss,
            "metadata": metadata,
        },
        checkpoint_path,
    )
    return checkpoint_path


def load_checkpoint(
    path: Path | str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
) -> dict[str, Any]:
    """Load a state dictionary into compatible objects without arbitrary pickles."""
    checkpoint = torch.load(Path(path), map_location="cpu", weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    if optimizer is not None:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    return checkpoint