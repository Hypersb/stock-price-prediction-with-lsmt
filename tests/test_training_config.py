import pytest
import torch

from ml.training.config import TrainingConfig


def test_training_config_defaults_and_cpu_device() -> None:
    config = TrainingConfig(device="cpu")

    assert config.epochs == 50
    assert config.seed == 42
    assert config.torch_device() == torch.device("cpu")


@pytest.mark.parametrize("field", ["epochs", "patience"])
def test_training_config_rejects_invalid_counts(field: str) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        TrainingConfig(**{field: 0})


def test_training_config_rejects_invalid_clipping() -> None:
    with pytest.raises(ValueError, match="gradient_clip_norm"):
        TrainingConfig(gradient_clip_norm=0)