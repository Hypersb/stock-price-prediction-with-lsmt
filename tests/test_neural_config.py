import pytest
import torch

from ml.neural.config import NeuralConfig, resolve_device


def test_neural_config_defaults_and_cpu_resolution() -> None:
    config = NeuralConfig()

    assert config.seed == 42
    assert resolve_device(prefer_accelerator=False) == torch.device("cpu")


@pytest.mark.parametrize("field", ["lookback", "input_size", "hidden_size", "num_layers", "batch_size"])
def test_neural_config_rejects_nonpositive_dimensions(field: str) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        NeuralConfig(**{field: 0})


def test_neural_config_rejects_invalid_dropout() -> None:
    with pytest.raises(ValueError, match="dropout"):
        NeuralConfig(dropout=1.0)