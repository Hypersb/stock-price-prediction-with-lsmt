"""PyTorch datasets for financial lookback sequences."""

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


class FinancialSequenceDataset(Dataset):
    """Store CPU sequence arrays and aligned targets for PyTorch loading."""

    def __init__(
        self,
        sequences: np.ndarray,
        targets: np.ndarray,
        target_dates: pd.DatetimeIndex | None = None,
    ) -> None:
        sequences_array = np.asarray(sequences, dtype=np.float32)
        targets_array = np.asarray(targets, dtype=np.float32)
        if sequences_array.ndim != 3:
            raise ValueError("sequences must have shape [samples, lookback, features]")
        if targets_array.ndim != 1 or len(sequences_array) != len(targets_array):
            raise ValueError("targets must align with sequence samples")
        if target_dates is not None and len(target_dates) != len(targets_array):
            raise ValueError("target_dates must align with sequence samples")
        self._sequences = torch.from_numpy(sequences_array)
        self._targets = torch.from_numpy(targets_array)
        self.target_dates = target_dates

    def __len__(self) -> int:
        return len(self._sequences)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self._sequences[index], self._targets[index]