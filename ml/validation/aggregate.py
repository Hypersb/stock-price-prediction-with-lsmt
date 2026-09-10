"""Aggregate fold metrics and quantify walk-forward stability."""

from dataclasses import dataclass

import numpy as np

from ml.validation.baselines import WalkForwardModelResult


@dataclass(frozen=True)
class StabilitySummary:
    """Aggregate metric summary for one model/task across folds."""

    model_name: str
    task: str
    fold_count: int
    metrics: dict[str, dict[str, float]]


def aggregate_fold_results(results: list[WalkForwardModelResult]) -> list[StabilitySummary]:
    """Calculate mean, standard deviation, minimum, and maximum per metric."""
    groups: dict[tuple[str, str], list[WalkForwardModelResult]] = {}
    for result in results:
        groups.setdefault((result.model_name, result.task), []).append(result)
    summaries = []
    for (model_name, task), grouped in groups.items():
        metric_names = {
            name
            for result in grouped
            for name, value in result.metrics.items()
            if isinstance(value, (int, float, np.integer, np.floating)) and np.isfinite(value)
        }
        metrics = {}
        for name in sorted(metric_names):
            values = np.asarray([result.metrics[name] for result in grouped], dtype=float)
            metrics[name] = {
                "mean": float(values.mean()),
                "std": float(values.std(ddof=0)),
                "min": float(values.min()),
                "max": float(values.max()),
            }
        summaries.append(StabilitySummary(model_name, task, len(grouped), metrics))
    return summaries