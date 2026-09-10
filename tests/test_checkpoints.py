from pathlib import Path

import torch

from ml.training.checkpoints import load_checkpoint, save_checkpoint


def test_checkpoint_round_trip(tmp_path: Path) -> None:
    model = torch.nn.Linear(2, 1)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    path = save_checkpoint(
        tmp_path / "checkpoint.pt",
        model,
        optimizer,
        epoch=3,
        validation_loss=0.25,
        metadata={"task": "regression", "lookback": 20},
    )
    restored = torch.nn.Linear(2, 1)
    restored_optimizer = torch.optim.Adam(restored.parameters(), lr=0.01)

    checkpoint = load_checkpoint(path, restored, restored_optimizer)

    assert checkpoint["epoch"] == 3
    assert checkpoint["metadata"]["task"] == "regression"
    assert all(torch.equal(left, right) for left, right in zip(model.parameters(), restored.parameters()))