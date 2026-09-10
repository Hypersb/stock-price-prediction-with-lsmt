"""Deterministic DataLoader utilities for temporal sequence datasets."""

from torch.utils.data import DataLoader

from ml.neural.dataset import FinancialSequenceDataset


def create_sequence_loader(
    dataset: FinancialSequenceDataset,
    batch_size: int,
) -> DataLoader:
    """Create a chronological, non-shuffling loader that keeps the final batch."""
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    return DataLoader(dataset, batch_size=batch_size, shuffle=False, drop_last=False)


def create_train_loader(dataset: FinancialSequenceDataset, batch_size: int) -> DataLoader:
    """Create the deterministic training loader."""
    return create_sequence_loader(dataset, batch_size)


def create_validation_loader(dataset: FinancialSequenceDataset, batch_size: int) -> DataLoader:
    """Create the deterministic validation loader."""
    return create_sequence_loader(dataset, batch_size)


def create_test_loader(dataset: FinancialSequenceDataset, batch_size: int) -> DataLoader:
    """Create the deterministic test loader."""
    return create_sequence_loader(dataset, batch_size)