"""Statistically responsible paired model comparison for time-series OOS predictions.

Prefer block bootstrap over naive i.i.d. assumptions. A nonsignificant difference
is not proof that two models are identical.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class StatisticalComparisonResult:
    """Block-bootstrap comparison of paired out-of-sample predictions."""

    model_a: str
    model_b: str
    metric: str
    observed_difference: float
    confidence_level: float
    confidence_interval: tuple[float, float]
    observations: int
    method: str
    block_length: int
    bootstrap_iterations: int
    seed: int
    notes: tuple[str, ...]


def compare_models_block_bootstrap(
    predictions: pd.DataFrame,
    *,
    model_a: str,
    model_b: str,
    metric: str = "mae",
    block_length: int = 5,
    bootstrap_iterations: int = 500,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> StatisticalComparisonResult:
    """Compare paired OOS predictions from two models over aligned dates.

    ``observed_difference`` is metric(model_a) - metric(model_b) on the full
    paired sample. Positive values mean model_a has a higher metric value.
    For error metrics (mae/mse/rmse), lower is better.
    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be in (0, 1)")
    if block_length <= 0 or bootstrap_iterations <= 0:
        raise ValueError("block_length and bootstrap_iterations must be positive")
    required = {"date", "model", "actual", "predicted"}
    if not required.issubset(predictions.columns):
        raise ValueError(f"predictions must contain {sorted(required)}")

    left = predictions.loc[predictions["model"] == model_a, ["date", "actual", "predicted"]]
    right = predictions.loc[predictions["model"] == model_b, ["date", "actual", "predicted"]]
    paired = left.merge(right, on="date", suffixes=("_a", "_b"))
    if paired.empty:
        raise ValueError("no aligned dates between the compared models")
    if not np.allclose(paired["actual_a"].to_numpy(), paired["actual_b"].to_numpy(), equal_nan=True):
        raise ValueError("paired actuals must match on aligned dates")

    actual = paired["actual_a"].to_numpy(dtype=float)
    pred_a = paired["predicted_a"].to_numpy(dtype=float)
    pred_b = paired["predicted_b"].to_numpy(dtype=float)
    pointwise = _pointwise_metric(actual, pred_a, pred_b, metric)
    observed = float(np.mean(pointwise))

    rng = np.random.default_rng(seed)
    samples = np.empty(bootstrap_iterations, dtype=float)
    n = len(pointwise)
    for index in range(bootstrap_iterations):
        resampled = _block_resample(pointwise, block_length=block_length, rng=rng, length=n)
        samples[index] = float(np.mean(resampled))

    alpha = 1.0 - confidence_level
    lower = float(np.quantile(samples, alpha / 2))
    upper = float(np.quantile(samples, 1.0 - alpha / 2))
    return StatisticalComparisonResult(
        model_a=model_a,
        model_b=model_b,
        metric=metric,
        observed_difference=observed,
        confidence_level=confidence_level,
        confidence_interval=(lower, upper),
        observations=n,
        method="moving_block_bootstrap",
        block_length=block_length,
        bootstrap_iterations=bootstrap_iterations,
        seed=seed,
        notes=(
            "difference is mean(model_a metric contribution - model_b metric contribution)",
            "block bootstrap respects temporal dependence only approximately",
            "a confidence interval covering zero does not prove the models are identical",
            "do not interpret nonsignificance as equivalence",
        ),
    )


def _pointwise_metric(
    actual: np.ndarray,
    pred_a: np.ndarray,
    pred_b: np.ndarray,
    metric: str,
) -> np.ndarray:
    if metric == "mae":
        return np.abs(pred_a - actual) - np.abs(pred_b - actual)
    if metric == "mse":
        return (pred_a - actual) ** 2 - (pred_b - actual) ** 2
    if metric == "rmse_proxy":
        # Pointwise squared-error difference; CI is on mean SE difference, not RMSE.
        return (pred_a - actual) ** 2 - (pred_b - actual) ** 2
    if metric == "directional_accuracy":
        hit_a = (np.sign(pred_a) == np.sign(actual)).astype(float)
        hit_b = (np.sign(pred_b) == np.sign(actual)).astype(float)
        return hit_a - hit_b
    if metric == "strategy_return_proxy":
        # Research diagnostic only: sign(prediction) * actual return difference.
        return np.sign(pred_a) * actual - np.sign(pred_b) * actual
    raise ValueError(f"unsupported metric: {metric}")


def _block_resample(
    values: np.ndarray,
    *,
    block_length: int,
    rng: np.random.Generator,
    length: int,
) -> np.ndarray:
    if len(values) <= block_length:
        indices = rng.integers(0, len(values), size=length)
        return values[indices]
    blocks_needed = int(np.ceil(length / block_length))
    starts = rng.integers(0, len(values) - block_length + 1, size=blocks_needed)
    pieces = [values[start : start + block_length] for start in starts]
    return np.concatenate(pieces)[:length]
