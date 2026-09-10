import pytest

from ml.backtesting.config import BacktestConfig


def test_backtest_config_defaults() -> None:
    config = BacktestConfig()

    assert config.strategy_mode == "long_only"
    assert config.initial_capital == 1.0


@pytest.mark.parametrize("field", ["transaction_cost_bps", "slippage_bps"])
def test_backtest_config_rejects_negative_costs(field: str) -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        BacktestConfig(**{field: -1})