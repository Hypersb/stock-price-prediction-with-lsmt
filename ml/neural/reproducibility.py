"""Reproducibility helpers for neural-network experiments."""

import random

import numpy as np
import torch


def set_random_seed(seed: int) -> None:
    """Seed Python, NumPy, and PyTorch random generators.

    Seeds improve computational experiment reproducibility but cannot make
    financial results deterministic across every platform and backend.
    """
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)