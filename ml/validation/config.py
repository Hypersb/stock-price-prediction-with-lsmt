"""Configuration for expanding and rolling walk-forward folds."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WalkForwardConfig:
    """Validated sizes and temporal controls for walk-forward evaluation."""

    window_type: str = "expanding"
    initial_train_size: int = 500
    validation_size: int = 100
    test_size: int = 100
    step_size: int = 100
    gap: int = 0
    forecast_horizon: int = 1
    maximum_train_size: int | None = None

    def __post_init__(self) -> None:
        if self.window_type not in {"expanding", "rolling"}:
            raise ValueError("window_type must be 'expanding' or 'rolling'")
        for name in ("initial_train_size", "validation_size", "test_size", "step_size"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if isinstance(self.gap, bool) or not isinstance(self.gap, int) or self.gap < 0:
            raise ValueError("gap must be a nonnegative integer")
        if isinstance(self.forecast_horizon, bool) or not isinstance(self.forecast_horizon, int) or self.forecast_horizon <= 0:
            raise ValueError("forecast_horizon must be a positive integer")
        if self.maximum_train_size is not None and (
            isinstance(self.maximum_train_size, bool)
            or not isinstance(self.maximum_train_size, int)
            or self.maximum_train_size <= 0
        ):
            raise ValueError("maximum_train_size must be a positive integer")
        if self.window_type == "rolling" and self.maximum_train_size is None:
            raise ValueError("rolling windows require maximum_train_size")