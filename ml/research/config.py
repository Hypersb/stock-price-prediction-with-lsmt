"""Reproducible configuration for the final research evaluation pipeline."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from ml.backtesting.config import BacktestConfig
from ml.research.regimes import RegimeConfig
from ml.research.universe import DEFAULT_RESEARCH_UNIVERSE, ResearchUniverse
from ml.validation.config import WalkForwardConfig


@dataclass(frozen=True)
class FinalResearchConfig:
    """Explicit experiment configuration; no silent scientifically material defaults.

    Callers must construct this object deliberately. Convenience builders may
    exist for tests, but production research should set every field consciously.
    """

    symbols: tuple[str, ...]
    target_type: str
    horizon: int
    feature_parameters: dict[str, object]
    walk_forward: WalkForwardConfig
    model_families: tuple[str, ...]
    random_seed: int
    lookback: int
    hidden_size: int
    lstm_epochs: int
    regime: RegimeConfig
    backtest: BacktestConfig
    cost_scenarios_bps: tuple[float, ...]
    signal_thresholds: tuple[float, ...]
    compare_model_a: str
    compare_model_b: str
    bootstrap_iterations: int
    block_length: int
    include_ablation: bool = True
    include_complexity: bool = True
    include_explainability: bool = True
    include_regimes: bool = True
    include_sensitivity: bool = True
    include_statistics: bool = True

    def __post_init__(self) -> None:
        if not self.symbols:
            raise ValueError("symbols must not be empty")
        if self.target_type not in {"regression", "direction"}:
            raise ValueError("target_type must be 'regression' or 'direction'")
        if self.horizon <= 0:
            raise ValueError("horizon must be positive")
        if self.random_seed < 0:
            raise ValueError("random_seed must be nonnegative")
        if not self.model_families:
            raise ValueError("model_families must not be empty")

    def fingerprint(self) -> str:
        """Stable configuration fingerprint for reproducible experiment identifiers."""
        payload = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict[str, object]:
        return {
            "symbols": list(self.symbols),
            "target_type": self.target_type,
            "horizon": self.horizon,
            "feature_parameters": self.feature_parameters,
            "walk_forward": asdict(self.walk_forward),
            "model_families": list(self.model_families),
            "random_seed": self.random_seed,
            "lookback": self.lookback,
            "hidden_size": self.hidden_size,
            "lstm_epochs": self.lstm_epochs,
            "regime": asdict(self.regime),
            "backtest": asdict(self.backtest),
            "cost_scenarios_bps": list(self.cost_scenarios_bps),
            "signal_thresholds": list(self.signal_thresholds),
            "compare_model_a": self.compare_model_a,
            "compare_model_b": self.compare_model_b,
            "bootstrap_iterations": self.bootstrap_iterations,
            "block_length": self.block_length,
            "include_ablation": self.include_ablation,
            "include_complexity": self.include_complexity,
            "include_explainability": self.include_explainability,
            "include_regimes": self.include_regimes,
            "include_sensitivity": self.include_sensitivity,
            "include_statistics": self.include_statistics,
        }


def tiny_fixture_config(
    symbols: tuple[str, ...] = ("SYN_A", "SYN_B"),
) -> FinalResearchConfig:
    """Deterministic small configuration for unit tests only."""
    return FinalResearchConfig(
        symbols=symbols,
        target_type="regression",
        horizon=1,
        feature_parameters={
            "return_lags": (1,),
            "momentum_windows": (3,),
            "moving_average_windows": (3,),
            "ema_spans": (3,),
            "volatility_windows": (3,),
            "volume_window": 3,
            "rsi_period": 3,
            "macd_fast": 2,
            "macd_slow": 4,
            "macd_signal": 2,
            "atr_period": 3,
        },
        walk_forward=WalkForwardConfig(
            initial_train_size=30,
            validation_size=8,
            test_size=8,
            step_size=20,
            forecast_horizon=1,
        ),
        model_families=("naive", "linear"),
        random_seed=7,
        lookback=3,
        hidden_size=4,
        lstm_epochs=1,
        regime=RegimeConfig(
            trend_ma_window=10,
            trend_return_window=5,
            volatility_window=5,
            volatility_min_history=20,
            min_observations_per_regime=5,
        ),
        backtest=BacktestConfig(transaction_cost_bps=0.0, slippage_bps=0.0),
        cost_scenarios_bps=(0.0, 10.0),
        signal_thresholds=(0.0,),
        compare_model_a="naive_regression",
        compare_model_b="linear_regression",
        bootstrap_iterations=50,
        block_length=3,
        include_ablation=True,
        include_complexity=True,
        include_explainability=False,
        include_regimes=True,
        include_sensitivity=True,
        include_statistics=True,
    )


def example_research_config() -> FinalResearchConfig:
    """Documented example configuration using the default research universe.

    This is an example only. It does not silently become the scientific default
    inside the pipeline; callers must pass a FinalResearchConfig explicitly.
    """
    universe = ResearchUniverse(symbols=DEFAULT_RESEARCH_UNIVERSE)
    return FinalResearchConfig(
        symbols=universe.symbols,
        target_type="regression",
        horizon=1,
        feature_parameters={},
        walk_forward=WalkForwardConfig(
            initial_train_size=252,
            validation_size=63,
            test_size=63,
            step_size=63,
            forecast_horizon=1,
        ),
        model_families=("naive", "linear", "tree", "lstm"),
        random_seed=42,
        lookback=20,
        hidden_size=32,
        lstm_epochs=10,
        regime=RegimeConfig(),
        backtest=BacktestConfig(transaction_cost_bps=10.0, slippage_bps=5.0),
        cost_scenarios_bps=(0.0, 5.0, 10.0, 25.0),
        signal_thresholds=(0.0,),
        compare_model_a="linear_regression",
        compare_model_b="lstm",
        bootstrap_iterations=500,
        block_length=10,
    )
