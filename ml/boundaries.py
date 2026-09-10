"""Explicit handling of feature warm-up and unavailable target tails."""

from dataclasses import dataclass

import pandas as pd

from ml.dataset import SupervisedFrame


@dataclass(frozen=True)
class BoundaryResult:
    """Model-ready data and auditable row-removal metadata."""

    frame: SupervisedFrame
    removed_dates: pd.Series
    feature_warmup_rows: int
    target_tail_rows: int
    overlapping_missing_rows: int


def prepare_model_ready(frame: SupervisedFrame) -> BoundaryResult:
    """Remove only rows with missing features or targets and retain audit details."""
    feature_missing = frame.X.isna().any(axis=1)
    target_missing = frame.y.isna()
    keep = ~(feature_missing | target_missing)
    removed = ~(keep)
    ready = SupervisedFrame(
        X=frame.X.loc[keep].copy(),
        y=frame.y.loc[keep].copy(),
        dates=frame.dates.loc[keep].copy(),
        feature_names=frame.feature_names,
    )
    return BoundaryResult(
        frame=ready,
        removed_dates=frame.dates.loc[removed].copy(),
        feature_warmup_rows=int((feature_missing & ~target_missing).sum()),
        target_tail_rows=int((target_missing & ~feature_missing).sum()),
        overlapping_missing_rows=int((feature_missing & target_missing).sum()),
    )