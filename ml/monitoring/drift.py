"""Distribution drift helpers (PSI and Kolmogorov–Smirnov).

These are diagnostic stubs: they compute scores from caller-supplied arrays
only and never invent baseline distributions or production traffic.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DriftReport:
    """Result of a single drift comparison."""

    method: str
    score: float
    threshold: float
    flagged: bool


def population_stability_index(
    expected: np.ndarray | list[float],
    actual: np.ndarray | list[float],
    *,
    bins: int = 10,
    threshold: float = 0.2,
    epsilon: float = 1e-6,
) -> DriftReport:
    """Compute Population Stability Index between two 1-d samples.

    PSI uses equal-width bins over the combined range. Empty inputs raise;
    this function never fabricates reference data.
    """
    exp = np.asarray(expected, dtype=float).ravel()
    act = np.asarray(actual, dtype=float).ravel()
    if exp.size == 0 or act.size == 0:
        raise ValueError("expected and actual must be non-empty")
    if bins < 2:
        raise ValueError("bins must be >= 2")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")

    lower = float(min(exp.min(), act.min()))
    upper = float(max(exp.max(), act.max()))
    if lower == upper:
        # Degenerate constant distributions — no bin width; PSI is 0.
        score = 0.0
        return DriftReport(
            method="psi",
            score=score,
            threshold=float(threshold),
            flagged=score >= threshold,
        )

    edges = np.linspace(lower, upper, bins + 1)
    exp_counts, _ = np.histogram(exp, bins=edges)
    act_counts, _ = np.histogram(act, bins=edges)
    exp_pct = exp_counts.astype(float) / exp_counts.sum()
    act_pct = act_counts.astype(float) / act_counts.sum()
    exp_pct = np.clip(exp_pct, epsilon, None)
    act_pct = np.clip(act_pct, epsilon, None)
    # Renormalize after clipping so percentages sum ~1.
    exp_pct = exp_pct / exp_pct.sum()
    act_pct = act_pct / act_pct.sum()
    score = float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))
    return DriftReport(
        method="psi",
        score=score,
        threshold=float(threshold),
        flagged=score >= threshold,
    )


def kolmogorov_smirnov(
    expected: np.ndarray | list[float],
    actual: np.ndarray | list[float],
    *,
    threshold: float = 0.1,
) -> DriftReport:
    """Two-sample KS statistic (max absolute CDF difference).

    Returns the KS distance only — no p-value fabrication. Caller supplies both
    samples; missing data is an error, not a silent pass.
    """
    exp = np.sort(np.asarray(expected, dtype=float).ravel())
    act = np.sort(np.asarray(actual, dtype=float).ravel())
    if exp.size == 0 or act.size == 0:
        raise ValueError("expected and actual must be non-empty")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")

    # Evaluate empirical CDFs on the pooled unique support.
    support = np.unique(np.concatenate([exp, act]))
    exp_cdf = np.searchsorted(exp, support, side="right") / exp.size
    act_cdf = np.searchsorted(act, support, side="right") / act.size
    score = float(np.max(np.abs(exp_cdf - act_cdf)))
    return DriftReport(
        method="ks",
        score=score,
        threshold=float(threshold),
        flagged=score >= threshold,
    )
