import pytest

from ml.validation.config import WalkForwardConfig


def test_walk_forward_config_defaults() -> None:
    config = WalkForwardConfig()

    assert config.window_type == "expanding"
    assert config.forecast_horizon == 1


@pytest.mark.parametrize("field", ["initial_train_size", "validation_size", "test_size", "step_size"])
def test_walk_forward_config_rejects_invalid_sizes(field: str) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        WalkForwardConfig(**{field: 0})


def test_walk_forward_config_requires_rolling_window_length() -> None:
    with pytest.raises(ValueError, match="maximum_train_size"):
        WalkForwardConfig(window_type="rolling")