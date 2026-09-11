"""Backtesting application service wrapping the Phase 10 engine."""

from __future__ import annotations

from datetime import date

import pandas as pd

from backend.app.core.errors import BadRequestError
from backend.app.core.json_utils import sanitize_mapping, to_iso_date, to_json_number
from backend.app.schemas.backtests import (
    BacktestRequest,
    BacktestResponse,
    EquityPoint,
)
from ml.backtesting.config import BacktestConfig
from ml.backtesting.engine import BacktestResult
from ml.backtesting.fold_aware import run_fold_aware_backtest


class BacktestService:
    """Run deterministic research backtests from explicit OOS payloads."""

    def run(self, request: BacktestRequest) -> BacktestResponse:
        if request.sample_kind != "out_of_sample":
            raise BadRequestError("only out_of_sample predictions are accepted")

        models = {item.model for item in request.predictions}
        tasks = {item.task.value for item in request.predictions}
        if len(models) != 1 or len(tasks) != 1:
            raise BadRequestError("predictions must share one model and one task")

        prediction_rows = []
        fold_values = {item.fold for item in request.predictions}
        has_fold_labels = any(item.fold is not None for item in request.predictions)
        if has_fold_labels and None in fold_values:
            raise BadRequestError("fold must be provided on every prediction when used")

        for item in request.predictions:
            row = {
                "date": item.date,
                "model": item.model,
                "task": item.task.value,
                "fold": int(item.fold) if item.fold is not None else 0,
            }
            if item.predicted is not None:
                row["predicted"] = item.predicted
            if item.probability is not None:
                row["probability"] = item.probability
            prediction_rows.append(row)

        predictions = pd.DataFrame(prediction_rows)
        predictions["date"] = pd.to_datetime(predictions["date"])
        market_returns = pd.DataFrame(
            [
                {"date": item.date, "realized_return": item.realized_return}
                for item in request.market_returns
            ]
        )
        market_returns["date"] = pd.to_datetime(market_returns["date"])

        config = BacktestConfig(
            strategy_mode=request.configuration.strategy_mode.value,
            signal_threshold=request.configuration.signal_threshold,
            transaction_cost_bps=request.configuration.transaction_cost_bps,
            slippage_bps=request.configuration.slippage_bps,
            annualization_factor=request.configuration.annualization_factor,
            initial_capital=request.configuration.initial_capital,
        )

        try:
            result = self._run_engine(predictions, market_returns, config, has_fold_labels)
        except ValueError as exc:
            raise BadRequestError(str(exc)) from exc

        timeline = result.timeline
        equity_curve = [
            EquityPoint(
                date=date.fromisoformat(to_iso_date(row["realization_date"])),
                equity=to_json_number(row["equity"]),
                net_strategy_return=to_json_number(row["net_strategy_return"]),
            )
            for _, row in timeline.iterrows()
        ]

        metrics = sanitize_mapping(dict(result.metrics))
        performance_keys = {
            "total_return",
            "annualized_return",
            "hit_rate",
        }
        risk_keys = {
            "annualized_volatility",
            "sharpe_ratio",
            "sortino_ratio",
            "maximum_drawdown",
        }
        performance_metrics = {
            key: metrics.get(key) for key in performance_keys if key in metrics
        }
        risk_metrics = {key: metrics.get(key) for key in risk_keys if key in metrics}
        # Include any remaining metrics under risk/performance buckets.
        for key, value in metrics.items():
            if key not in performance_metrics and key not in risk_metrics:
                risk_metrics[key] = value

        analytics = sanitize_mapping(dict(result.analytics))
        benchmark = {
            name: sanitize_mapping(dict(values))
            for name, values in result.benchmark.items()
        }

        start_date = equity_curve[0].date if equity_curve else None
        end_date = equity_curve[-1].date if equity_curve else None

        return BacktestResponse(
            symbol=request.symbol,
            model=result.model,
            task=result.task,
            sample_kind="out_of_sample",
            configuration=request.configuration,
            start_date=start_date,
            end_date=end_date,
            observations=result.observations,
            performance_metrics=performance_metrics,
            risk_metrics=risk_metrics,
            trading_analytics=analytics,
            benchmark_metrics=benchmark,
            equity_curve=equity_curve,
        )

    def _run_engine(
        self,
        predictions: pd.DataFrame,
        market_returns: pd.DataFrame,
        config: BacktestConfig,
        has_fold_labels: bool,
    ) -> BacktestResult:
        """Prefer fold-aware evaluation so discontinuous OOS series are not annualized silently."""
        fold_count = int(predictions["fold"].nunique())
        if has_fold_labels or fold_count > 1:
            fold_aware = run_fold_aware_backtest(predictions, market_returns, config)
            if fold_aware.combined is not None:
                return fold_aware.combined
            if len(fold_aware.fold_results) == 1:
                return fold_aware.fold_results[0].result
            raise ValueError(
                "discontinuous or overlapping multi-fold OOS predictions cannot be returned "
                "as one continuous annualized backtest; provide a trading-day-contiguous "
                "series or a single fold"
            )

        # Untagged single series: still reject missing business days before annualizing.
        tagged = predictions.copy()
        tagged["fold"] = 0
        fold_aware = run_fold_aware_backtest(tagged, market_returns, config)
        if fold_aware.combined is None:
            raise ValueError(
                "prediction dates are not trading-day contiguous; combined annualized "
                "metrics would be misleading"
            )
        return fold_aware.combined
