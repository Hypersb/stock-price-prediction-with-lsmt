import numpy as np
import torch

from ml.neural.dataset import FinancialSequenceDataset
from ml.neural.loaders import create_sequence_loader
from ml.neural.lstm import LSTMRegressor
from ml.training.epochs import train_epoch
from ml.training.optimization import create_loss, create_optimizer


def test_train_epoch_updates_model_parameters() -> None:
    dataset = FinancialSequenceDataset(np.ones((4, 3, 2)), np.ones(4))
    loader = create_sequence_loader(dataset, 1)
    model = LSTMRegressor(input_size=2, hidden_size=4)
    before = [parameter.detach().clone() for parameter in model.parameters()]

    loss = train_epoch(
        model, loader, create_optimizer(model.parameters()), create_loss("regression"), torch.device("cpu"), 1.0
    )

    assert np.isfinite(loss)
    assert any(not torch.equal(old, new) for old, new in zip(before, model.parameters()))