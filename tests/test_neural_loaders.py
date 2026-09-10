import numpy as np
import torch

from ml.neural.dataset import FinancialSequenceDataset
from ml.neural.loaders import create_sequence_loader


def test_loader_preserves_order_and_final_partial_batch() -> None:
    dataset = FinancialSequenceDataset(np.arange(15).reshape(5, 3, 1), np.arange(5))
    loader = create_sequence_loader(dataset, batch_size=2)

    batches = list(loader)

    assert len(batches) == 3
    assert batches[0][1].tolist() == [0.0, 1.0]
    assert batches[-1][0].shape == torch.Size([1, 3, 1])
    assert batches[-1][1].tolist() == [4.0]


def test_loader_rejects_invalid_batch_size() -> None:
    dataset = FinancialSequenceDataset(np.ones((1, 2, 1)), np.ones(1))
    try:
        create_sequence_loader(dataset, 0)
    except ValueError as error:
        assert "positive integer" in str(error)
    else:
        raise AssertionError("invalid batch size should fail")