"""Backtest sensitivity analysis across costs and signal thresholds.

Threshold sweeps are diagnostic. Do not select the best threshold on the final
test period and report it as unbiased performance. If threshold selection is
required, use training/validation information only.
"""

from dataclasses import dataclass, replace

import pandas as pd

from ml.backtesting.config import BacktestConfig
from ml.backtesting.engine import run_backtest
from ml.backtesting.returns import calculate_strategy_returns

DEFAULT_COST_SCENARIOS_BPS: tuple[float, ...] = (0.0, 5.0, 10.0, 25.0)


@dataclass(frozen=True)
class SensitivityRow:
    """One sensitivity configuration and its economic diagnostics."""

    configuration: str
    transaction_cost_bps: float
    slippage_bps: float
    signal_threshold: float
    gross_return: float
    net_return: float
    sharpe: float
    sortino: float
    maximum_drawdown: float
    turnover: float
    trade_count: int
    notes: tuple[str, ...]


@dataclass(frozen=True)
class SensitivityResult:
    """Sensitivity table across cost and optional threshold scenarios."""

    rows: tuple[SensitivityRow, ...]
    notes: tuple[str, ...]

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "configuration": row.configuration,
                    "transaction_cost_bps": row.transaction_cost_bps,
                    "slippage_bps": row.slippage_bps,
                    "signal_threshold": row.signal_threshold,
                    "gross_return": row.gross_return,
                    "net_return": row.net_return,
                    "sharpe": row.sharpe,
                    "sortino": row.sortino,
                    "maximum_drawdown": row.maximum_drawdown,
                    "turnover": row.turnover,
                    "trade_count": row.trade_count,
                }
                for row in self.rows
            ]
        )


def run_backtest_sensitivity(
    out_of_sample_predictions: pd.DataFrame,
    market_returns: pd.DataFrame,
    *,
    base_config: BacktestConfig | None = None,
    cost_scenarios_bps: tuple[float, ...] = DEFAULT_COST_SCENARIOS_BPS,
    slippage_bps: float = 0.0,
    signal_thresholds: tuple[float, ...] | None = None,
) -> SensitivityResult:
    """Evaluate an otherwise identical strategy under multiple cost assumptions.

    Signal-threshold sensitivity is optional and diagnostic only. Thresholds
    must not be chosen on the final holdout and then reported as unbiased.
    """
    base = base_config or BacktestConfig()
    thresholds = signal_thresholds if signal_thresholds is not None else (base.signal_threshold,)
    rows: list[SensitivityRow] = []
    for threshold in thresholds:
        for cost in cost_scenarios_bps:
            config = replace(
                base,
                transaction_cost_bps=float(cost),
                slippage_bps=float(slippage_bps),
                signal_threshold=float(threshold),
            )
            result = run_backtest(out_of_sample_predictions, market_returns, config)
            rows.append(
                SensitivityRow(
                    configuration=(
                        f"cost_{cost:g}bps_slip_{slippage_bps:g}bps_thresh_{threshold:g}"
                    ),
                    transaction_cost_bps=float(cost),
                    slippage_bps=float(slippage_bps),
                    signal_threshold=float(threshold),
                    gross_return=float(
                        (1 + result.timeline["gross_strategy_return"]).prod() - 1
                    ),
                    net_return=float(result.metrics["total_return"]),
                    sharpe=float(result.metrics["sharpe_ratio"]),
                    sortino=float(result.metrics["sortino_ratio"]),
                    maximum_drawdown=float(result.metrics["maximum_drawdown"]),
                    turnover=float(result.timeline["turnover"].sum()),
                    trade_count=int(result.analytics.get("completed_trades", 0)),
                    notes=(
                        "threshold sensitivity is diagnostic, not unbiased selection",
                        "do not tune thresholds on the final test period",
                    ),
                )
            )
    return SensitivityResult(
        rows=tuple(rows),
        notes=(
            "higher transaction costs cannot increase net return for an identical position path",
            "threshold sweeps are diagnostics; selection belongs on train/validation only",
            "apparent performance often deteriorates as costs rise",
        ),
    )


def net_return_for_fixed_positions(
    positions: pd.Series,
    realized_returns: pd.Series,
    *,
    transaction_cost_bps: float,
    slippage_bps: float = 0.0,
) -> float:
    """Helper used by tests to compare net returns under rising costs."""
    frame = calculate_strategy_returns(
        positions,
        realized_returns,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
    )
    return float((1 + frame["net_strategy_return"]).prod() - 1)
