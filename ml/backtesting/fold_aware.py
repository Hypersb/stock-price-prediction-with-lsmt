"""Fold-aware out-of-sample backtesting with explicit timeline diagnostics.

Walk-forward OOS predictions must not be silently treated as one continuous
daily portfolio when folds contain gaps or overlapping realization periods.

Annualized metrics for a combined series are only returned when the aligned
realization timeline is calendar-contiguous and free of cross-fold overlaps.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml.backtesting.config import BacktestConfig
from ml.backtesting.engine import BacktestResult, run_backtest


@dataclass(frozen=True)
class OOSTimelineReport:
    """Diagnostics for stitched walk-forward prediction dates."""

    observation_count: int
    unique_prediction_dates: int
    overlapping_prediction_dates: tuple[str, ...]
    max_gap_days: int
    is_calendar_contiguous: bool
    allows_combined_continuous_backtest: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class FoldBacktestResult:
    """One fold's independent historical simulation."""

    fold: int
    result: BacktestResult


@dataclass(frozen=True)
class FoldAwareBacktestResult:
    """Per-fold backtests plus optional combined continuous metrics."""

    model: str
    task: str
    fold_results: tuple[FoldBacktestResult, ...]
    combined: BacktestResult | None
    aggregate_metrics: dict[str, float]
    timeline: OOSTimelineReport
    annualization_assumptions: tuple[str, ...]


def analyze_oos_prediction_timeline(predictions: pd.DataFrame) -> OOSTimelineReport:
    """Detect overlaps and calendar gaps across fold-tagged OOS predictions."""
    required = {"date", "fold", "model", "task"}
    if not required.issubset(predictions.columns):
        raise ValueError(f"predictions must contain {sorted(required)}")
    if predictions.empty:
        raise ValueError("predictions must not be empty")

    frame = predictions.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    if frame.duplicated(subset=["date", "fold", "model", "task"]).any():
        raise ValueError("duplicate prediction records within the same fold are not allowed")

    date_fold_counts = frame.groupby("date")["fold"].nunique()
    overlapping = date_fold_counts[date_fold_counts > 1]
    overlapping_dates = tuple(sorted(overlapping.index.strftime("%Y-%m-%d")))

    unique_dates = pd.DatetimeIndex(sorted(frame["date"].unique()))
    if len(unique_dates) <= 1:
        max_gap_days = 0
        contiguous = True
    else:
        gaps = np.diff(unique_dates.values).astype("timedelta64[D]").astype(int)
        max_gap_days = int(gaps.max()) if len(gaps) else 0
        contiguous = bool((gaps == 1).all())

    allows_combined = len(overlapping_dates) == 0 and contiguous
    notes = [
        "annualized combined metrics require contiguous unique realization calendar dates",
        "overlapping prediction dates across folds reject combined continuous backtests",
        "per-fold backtests preserve fold identity regardless of stitching validity",
    ]
    if overlapping_dates:
        notes.append(f"overlapping prediction dates across folds: {len(overlapping_dates)}")
    if not contiguous:
        notes.append(f"max calendar gap between unique prediction dates is {max_gap_days} day(s)")

    return OOSTimelineReport(
        observation_count=len(frame),
        unique_prediction_dates=len(unique_dates),
        overlapping_prediction_dates=overlapping_dates,
        max_gap_days=max_gap_days,
        is_calendar_contiguous=contiguous,
        allows_combined_continuous_backtest=allows_combined,
        notes=tuple(notes),
    )


def run_fold_aware_backtest(
    predictions: pd.DataFrame,
    market_returns: pd.DataFrame,
    config: BacktestConfig,
    *,
    allow_combined_when_contiguous: bool = True,
) -> FoldAwareBacktestResult:
    """Run per-fold backtests and optionally a combined continuous backtest.

    Raises ``ValueError`` when a combined continuous backtest is requested but
    the timeline has overlapping prediction dates across folds. Gapped timelines
    do not raise; they simply omit combined annualized metrics.
    """
    if predictions.empty:
        raise ValueError("predictions must not be empty")
    timeline = analyze_oos_prediction_timeline(predictions)
    if timeline.overlapping_prediction_dates:
        raise ValueError(
            "overlapping out-of-sample prediction dates across folds prevent a "
            "well-defined combined continuous backtest; run per-fold only or "
            "resolve duplicate dates"
        )

    model = str(predictions["model"].iloc[0])
    task = str(predictions["task"].iloc[0])
    fold_results: list[FoldBacktestResult] = []
    for fold_id, group in predictions.groupby("fold", sort=True):
        fold_results.append(
            FoldBacktestResult(
                fold=int(fold_id),
                result=run_backtest(group, market_returns, config),
            )
        )

    combined: BacktestResult | None = None
    annualization_valid = False
    assumptions: list[str] = [
        "sharpe/sortino annualization assumes consecutive trading observations",
        "combined continuous backtest is emitted only for contiguous non-overlapping timelines",
        "per-fold aggregate metrics average fold-level totals without inventing continuity",
    ]
    if allow_combined_when_contiguous and timeline.allows_combined_continuous_backtest:
        combined = run_backtest(predictions, market_returns, config)
        annualization_valid = True
        assumptions.append(
            "combined series passed contiguous unique-date checks; annualization may be interpreted as continuous"
        )
    else:
        assumptions.append(
            "combined continuous annualized metrics omitted because the OOS timeline is discontinuous"
        )

    aggregate = _aggregate_fold_metrics(fold_results)
    aggregate["annualization_valid_for_combined"] = float(annualization_valid)
    return FoldAwareBacktestResult(
        model=model,
        task=task,
        fold_results=tuple(fold_results),
        combined=combined,
        aggregate_metrics=aggregate,
        timeline=timeline,
        annualization_assumptions=tuple(assumptions),
    )


def _aggregate_fold_metrics(fold_results: list[FoldBacktestResult]) -> dict[str, float]:
    if not fold_results:
        return {}
    keys = sorted(
        {
            key
            for item in fold_results
            for key, value in item.result.metrics.items()
            if isinstance(value, (int, float, np.floating)) and not isinstance(value, bool)
        }
    )
    aggregate: dict[str, float] = {"fold_count": float(len(fold_results))}
    for key in keys:
        values = [float(item.result.metrics[key]) for item in fold_results]
        aggregate[f"mean_{key}"] = float(np.mean(values))
        aggregate[f"std_{key}"] = float(np.std(values, ddof=0))
    return aggregate
