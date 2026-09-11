"""Tests for fold-aware discontinuous OOS backtesting."""

import numpy as np
import pandas as pd
import pytest

from ml.backtesting.config import BacktestConfig
from ml.backtesting.fold_aware import (
    analyze_oos_prediction_timeline,
    run_fold_aware_backtest,
)


def _preds(dates, folds, model="m", task="regression") -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(dates),
            "fold": folds,
            "model": model,
            "task": task,
            "actual": np.linspace(-0.01, 0.01, len(dates)),
            "predicted": np.linspace(-0.008, 0.012, len(dates)),
        }
    )


def _market(dates) -> pd.DataFrame:
    dates = pd.to_datetime(dates)
    return pd.DataFrame(
        {
            "date": dates,
            "realized_return": np.linspace(-0.01, 0.01, len(dates)),
        }
    )


def test_overlapping_fold_dates_are_detected_and_reject_combined_backtest() -> None:
    dates = pd.date_range("2020-01-01", periods=6, freq="D")
    predictions = pd.concat(
        [
            _preds(dates[:4], [0] * 4),
            _preds(dates[2:6], [1] * 4),
        ],
        ignore_index=True,
    )
    report = analyze_oos_prediction_timeline(predictions)
    assert report.overlapping_prediction_dates
    assert report.allows_combined_continuous_backtest is False

    market = _market(pd.date_range("2020-01-01", periods=8, freq="D"))
    with pytest.raises(ValueError, match="overlapping"):
        run_fold_aware_backtest(predictions, market, BacktestConfig())


def test_gapped_folds_run_per_fold_without_combined_annualization() -> None:
    # Two contiguous folds separated by a gap (step > test).
    fold0_dates = pd.date_range("2020-01-01", periods=4, freq="D")
    fold1_dates = pd.date_range("2020-01-20", periods=4, freq="D")
    predictions = pd.concat(
        [
            _preds(fold0_dates, [0] * 4),
            _preds(fold1_dates, [1] * 4),
        ],
        ignore_index=True,
    )
    market = _market(pd.date_range("2020-01-01", periods=40, freq="D"))
    report = analyze_oos_prediction_timeline(predictions)
    assert report.is_calendar_contiguous is False
    assert report.max_gap_days >= 2
    assert report.allows_combined_continuous_backtest is False

    result = run_fold_aware_backtest(predictions, market, BacktestConfig())
    assert len(result.fold_results) == 2
    assert result.combined is None
    assert result.aggregate_metrics["fold_count"] == 2.0
    assert result.aggregate_metrics["annualization_valid_for_combined"] == 0.0
    assert any("discontinuous" in note for note in result.annualization_assumptions)


def test_contiguous_nonoverlapping_folds_allow_combined_backtest() -> None:
    dates = pd.date_range("2020-01-01", periods=8, freq="D")
    predictions = pd.concat(
        [
            _preds(dates[:4], [0] * 4),
            _preds(dates[4:], [1] * 4),
        ],
        ignore_index=True,
    )
    market = _market(pd.date_range("2020-01-01", periods=12, freq="D"))
    result = run_fold_aware_backtest(predictions, market, BacktestConfig())
    assert result.timeline.allows_combined_continuous_backtest is True
    assert result.combined is not None
    assert result.aggregate_metrics["annualization_valid_for_combined"] == 1.0
    assert "prediction_date" in result.combined.timeline.columns or "realization_date" in result.combined.timeline.columns
