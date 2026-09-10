import torch
from torch import nn

from ml.training.optimization import create_loss, create_optimizer


def test_optimization_factories_create_task_losses_and_optimizer() -> None:
    model = nn.Linear(2, 1)
    regression_loss = create_loss("regression")
    classification_loss = create_loss("classification")
    optimizer = create_optimizer(model.parameters())

    assert isinstance(regression_loss, nn.MSELoss)
    assert isinstance(classification_loss, nn.BCEWithLogitsLoss)
    logits = model(torch.ones(2, 2)).squeeze(-1)
    classification_loss(logits, torch.ones(2)).backward()
    optimizer.step()


def test_optimization_rejects_unknown_task() -> None:
    try:
        create_loss("unknown")
    except ValueError as error:
        assert "task" in str(error)
    else:
        raise AssertionError("unknown task should fail")