"""Single-epoch training and validation operations."""

import torch
from torch import nn
from torch.nn.utils import clip_grad_norm_
from torch.utils.data import DataLoader


def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    gradient_clip_norm: float | None = None,
) -> float:
    """Train on one loader and return sample-weighted mean loss."""
    model.train()
    total_loss = 0.0
    total_samples = 0
    for features, targets in loader:
        features = features.to(device)
        targets = targets.to(device)
        optimizer.zero_grad(set_to_none=True)
        predictions = model(features)
        loss = criterion(predictions, targets)
        loss.backward()
        if gradient_clip_norm is not None:
            clip_grad_norm_(model.parameters(), gradient_clip_norm)
        optimizer.step()
        batch_size = len(features)
        total_loss += loss.item() * batch_size
        total_samples += batch_size
    if total_samples == 0:
        raise ValueError("training loader must contain at least one sample")
    return total_loss / total_samples