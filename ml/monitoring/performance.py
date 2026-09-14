"""Rolling prediction-error monitoring without fabricated metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

PerformanceStatus = Literal["ok", "insufficient_data"]


@dataclass(frozen=True)
class PerformanceReport:
    """Rolling MAE/RMSE over aligned prediction/actual pairs."""

    status: PerformanceStatus
    window: int
    n_observations: int
    mae: float | None
    rmse: float | None
    message: str = ""


def rolling_error_metrics(
    predictions: np.ndarray | list[float],
    actuals: np.ndarray | list[float],
    *,
    window: int = 20,
    min_observations: int | None = None,
) -> PerformanceReport:
    """Compute MAE and RMSE over the most recent ``window`` aligned pairs.

    If fewer than ``min_observations`` (default: ``window``) finite pairs are
    available, returns ``status="insufficient_data"`` with null metrics rather
    than inventing values.
    """
    pred = np.asarray(predictions, dtype=float).ravel()
    act = np.asarray(actuals, dtype=float).ravel()
    if pred.shape != act.shape:
        raise ValueError("predictions and actuals must have the same length")
    if window <= 0:
        raise ValueError("window must be positive")
    required = window if min_observations is None else int(min_observations)
    if required <= 0:
        raise ValueError("min_observations must be positive")

    mask = np.isfinite(pred) & np.isfinite(act)
    paired_pred = pred[mask]
    paired_act = act[mask]
    n = int(paired_pred.size)
    if n < required:
        return PerformanceReport(
            status="insufficient_data",
            window=window,
            n_observations=n,
            mae=None,
            rmse=None,
            message=f"need at least {required} finite pairs; got {n}",
        )

    recent_pred = paired_pred[-window:]
    recent_act = paired_act[-window:]
    errors = recent_pred - recent_act
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors**2)))
    return PerformanceReport(
        status="ok",
        window=window,
        n_observations=n,
        mae=mae,
        rmse=rmse,
        message="rolling error metrics from provided series",
    )
