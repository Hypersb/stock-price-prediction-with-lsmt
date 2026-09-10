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


def validate_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, torch.Tensor, torch.Tensor]:
    """Evaluate one loader without gradients or parameter updates."""
    model.eval()
    total_loss = 0.0
    total_samples = 0
    predictions: list[torch.Tensor] = []
    targets_seen: list[torch.Tensor] = []
    with torch.no_grad():
        for features, targets in loader:
            features = features.to(device)
            targets = targets.to(device)
            batch_predictions = model(features)
            loss = criterion(batch_predictions, targets)
            batch_size = len(features)
            total_loss += loss.item() * batch_size
            total_samples += batch_size
            predictions.append(batch_predictions.detach().cpu())
            targets_seen.append(targets.detach().cpu())
    if total_samples == 0:
        raise ValueError("validation loader must contain at least one sample")
    return total_loss / total_samples, torch.cat(predictions), torch.cat(targets_seen)