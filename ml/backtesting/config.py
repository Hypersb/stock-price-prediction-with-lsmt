"""Configuration for historical strategy simulation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestConfig:
    """Validated assumptions for a deterministic research backtest."""

    strategy_mode: str = "long_only"
    signal_threshold: float = 0.0
    transaction_cost_bps: float = 0.0
    slippage_bps: float = 0.0
    annualization_factor: float = 252.0
    initial_capital: float = 1.0

    def __post_init__(self) -> None:
        if self.strategy_mode not in {"long_only", "long_short"}:
            raise ValueError("strategy_mode must be 'long_only' or 'long_short'")
        if self.signal_threshold < 0:
            raise ValueError("signal_threshold must be nonnegative")
        if self.transaction_cost_bps < 0 or self.slippage_bps < 0:
            raise ValueError("costs must be nonnegative")
        if self.annualization_factor <= 0:
            raise ValueError("annualization_factor must be positive")
        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be positive")