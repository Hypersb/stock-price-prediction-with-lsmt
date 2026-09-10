import torch
from torch import nn

from ml.training.early_stopping import EarlyStopping


def test_early_stopping_tracks_and_restores_best_state() -> None:
    model = nn.Linear(1, 1)
    stopping = EarlyStopping(patience=2)
    losses = [0.50, 0.40, 0.39, 0.40, 0.42]
    stopped = []
    for epoch, loss in enumerate(losses, 1):
        with torch.no_grad():
            model.weight.fill_(float(epoch))
        stopped.append(stopping.update(loss, epoch, model))

    assert stopping.best_epoch == 3
    assert stopping.best_loss == 0.39
    assert stopped[-1] is True
    with torch.no_grad():
        model.weight.fill_(99.0)
    stopping.restore(model)
    assert model.weight.item() == 3.0