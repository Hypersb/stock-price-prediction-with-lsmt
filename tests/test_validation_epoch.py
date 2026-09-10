import numpy as np
import torch

from ml.neural.dataset import FinancialSequenceDataset
from ml.neural.loaders import create_sequence_loader
from ml.neural.lstm import LSTMRegressor
from ml.training.epochs import validate_epoch
from ml.training.optimization import create_loss


def test_validation_epoch_does_not_update_parameters() -> None:
    dataset = FinancialSequenceDataset(np.ones((3, 2, 1)), np.ones(3))
    model = LSTMRegressor(input_size=1, hidden_size=3)
    before = [parameter.detach().clone() for parameter in model.parameters()]

    loss, predictions, targets = validate_epoch(
        model, create_sequence_loader(dataset, 2), create_loss("regression"), torch.device("cpu")
    )

    assert np.isfinite(loss)
    assert predictions.shape == torch.Size([3])
    assert targets.shape == torch.Size([3])
    assert all(torch.equal(old, new) for old, new in zip(before, model.parameters()))