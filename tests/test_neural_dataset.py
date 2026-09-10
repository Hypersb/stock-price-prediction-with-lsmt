import numpy as np
import pandas as pd
import torch

from ml.neural.dataset import FinancialSequenceDataset


def test_financial_sequence_dataset_returns_float32_tensors() -> None:
    dates = pd.DatetimeIndex(pd.date_range("2020-01-01", periods=2))
    dataset = FinancialSequenceDataset(np.ones((2, 3, 4)), np.array([0, 1]), dates)

    sequence, target = dataset[1]

    assert len(dataset) == 2
    assert sequence.shape == (3, 4)
    assert target.shape == torch.Size([])
    assert sequence.dtype == torch.float32
    assert target.dtype == torch.float32
    assert dataset.target_dates[1] == dates[1]