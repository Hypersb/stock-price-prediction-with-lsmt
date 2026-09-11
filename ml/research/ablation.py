"""Feature-group ablation experiments with aligned evaluation methodology.

Ablations reuse the same dates, targets, and chronological evaluation protocol.
Tiny metric differences are reported numerically but are not automatically
interpreted as meaningful.
"""

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml.dataset import SupervisedFrame
from ml.evaluation.classification import evaluate_classification
from ml.evaluation.regression import evaluate_regression
from ml.models.classification import LogisticDirectionModel
from ml.models.regression import LinearRegressionModel
from ml.preprocessing import TrainOnlyScaler
from ml.research.dataset_prep import prepare_research_frame
from ml.split_validation import validate_temporal_split
from ml.splitting import chronological_split

FEATURE_GROUPS: dict[str, tuple[str, ...]] = {
    "returns": ("simple_return", "log_return", "return_lag_"),
    "momentum": ("momentum_",),
    "trend": ("sma_", "close_to_sma_", "ema_", "close_to_ema_"),
    "volatility": ("volatility_", "atr_"),
    "volume": ("volume_change", "volume_lag_", "volume_sma_", "relative_volume_"),
    "technical": ("rsi_", "macd", "macd_signal", "macd_histogram"),
}


@dataclass(frozen=True)
class AblationResult:
    """One ablation experiment compared against the full-feature baseline."""

    experiment: str
    included_groups: tuple[str, ...]
    excluded_groups: tuple[str, ...]
    feature_count: int
    baseline_metrics: dict[str, float]
    ablated_metrics: dict[str, float]
    absolute_change: dict[str, float]
    relative_change: dict[str, float]
    observations: int
    notes: tuple[str, ...]


def feature_names_for_groups(
    all_feature_names: Iterable[str],
    groups: Iterable[str],
) -> tuple[str, ...]:
    """Select feature columns belonging to the named logical groups."""
    selected_groups = tuple(groups)
    unknown = sorted(set(selected_groups) - set(FEATURE_GROUPS))
    if unknown:
        raise ValueError(f"unknown feature groups: {unknown}")
    patterns = [pattern for group in selected_groups for pattern in FEATURE_GROUPS[group]]
    selected: list[str] = []
    for name in all_feature_names:
        if any(name == pattern or name.startswith(pattern) for pattern in patterns):
            selected.append(name)
    return tuple(dict.fromkeys(selected))


def exclude_feature_groups(
    all_feature_names: Iterable[str],
    excluded_groups: Iterable[str],
) -> tuple[str, ...]:
    """Return all features except those matching excluded groups."""
    excluded = set(feature_names_for_groups(all_feature_names, excluded_groups))
    return tuple(name for name in all_feature_names if name not in excluded)


def run_feature_ablation_study(
    ohlcv: pd.DataFrame,
    *,
    symbol: str = "SYN",
    target_type: str = "regression",
    horizon: int = 1,
    feature_parameters: dict[str, object] | None = None,
    excluded_group_experiments: tuple[str, ...] | None = None,
    include_single_group_only: bool = False,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
    test_fraction: float = 0.15,
) -> tuple[AblationResult, ...]:
    """Run aligned leave-group-out (and optional single-group) ablations.

    The baseline and every ablation share the same chronological split dates and
    target definition. Models are refit on the ablated feature subset only.
    Evaluation uses the validation partition so the final test holdout remains
    unused for ablation diagnostics.
    """
    frame = prepare_research_frame(
        ohlcv,
        symbol=symbol,
        target_type=target_type,
        horizon=horizon,
        feature_parameters=feature_parameters,
    )
    supervised = SupervisedFrame(
        X=frame.X,
        y=frame.y,
        dates=frame.dates,
        feature_names=frame.feature_names,
    )
    split = chronological_split(supervised, train_fraction, validation_fraction, test_fraction)
    validate_temporal_split(split)

    baseline_metrics = _fit_and_evaluate(
        split.train.X,
        split.train.y,
        split.validation.X,
        split.validation.y,
        task=frame.task,
    )
    experiments = excluded_group_experiments or tuple(FEATURE_GROUPS.keys())
    results: list[AblationResult] = []

    for group in experiments:
        kept = exclude_feature_groups(frame.feature_names, (group,))
        if not kept:
            continue
        ablated_metrics = _fit_and_evaluate(
            split.train.X.loc[:, kept],
            split.train.y,
            split.validation.X.loc[:, kept],
            split.validation.y,
            task=frame.task,
        )
        results.append(
            _comparison(
                experiment=f"all_minus_{group}",
                included_groups=tuple(g for g in FEATURE_GROUPS if g != group),
                excluded_groups=(group,),
                feature_count=len(kept),
                baseline_metrics=baseline_metrics,
                ablated_metrics=ablated_metrics,
                observations=len(split.validation.y),
                notes=(
                    "validation-only ablation diagnostics; test holdout unused",
                    "tiny differences are not automatically meaningful",
                    f"shared_validation_rows={len(split.validation.y)}",
                ),
            )
        )

    if include_single_group_only:
        for group in experiments:
            only = feature_names_for_groups(frame.feature_names, (group,))
            if not only:
                continue
            ablated_metrics = _fit_and_evaluate(
                split.train.X.loc[:, only],
                split.train.y,
                split.validation.X.loc[:, only],
                split.validation.y,
                task=frame.task,
            )
            results.append(
                _comparison(
                    experiment=f"only_{group}",
                    included_groups=(group,),
                    excluded_groups=tuple(g for g in FEATURE_GROUPS if g != group),
                    feature_count=len(only),
                    baseline_metrics=baseline_metrics,
                    ablated_metrics=ablated_metrics,
                    observations=len(split.validation.y),
                    notes=(
                        "single feature-group experiment on the same validation dates",
                        "tiny differences are not automatically meaningful",
                    ),
                )
            )

    return tuple(results)


def _fit_and_evaluate(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_validation: pd.DataFrame,
    y_validation: pd.Series,
    *,
    task: str,
) -> dict[str, float]:
    scaler = TrainOnlyScaler.create()
    X_train_scaled = scaler.fit_transform(X_train)
    X_validation_scaled = scaler.transform(X_validation)
    if task == "regression":
        model = LinearRegressionModel().fit(X_train_scaled, y_train)
        metrics = evaluate_regression(y_validation, model.predict(X_validation_scaled))
    else:
        model = LogisticDirectionModel().fit(X_train_scaled, y_train)
        predicted = model.predict(X_validation_scaled)
        probabilities = model.predict_proba(X_validation_scaled)
        metrics = evaluate_classification(y_validation, predicted, probabilities)
    return {
        key: float(value)
        for key, value in metrics.items()
        if isinstance(value, (int, float, np.floating)) and not isinstance(value, bool)
    }


def _comparison(
    *,
    experiment: str,
    included_groups: tuple[str, ...],
    excluded_groups: tuple[str, ...],
    feature_count: int,
    baseline_metrics: dict[str, float],
    ablated_metrics: dict[str, float],
    observations: int,
    notes: tuple[str, ...],
) -> AblationResult:
    keys = sorted(set(baseline_metrics) & set(ablated_metrics))
    absolute = {key: ablated_metrics[key] - baseline_metrics[key] for key in keys}
    relative = {
        key: (
            (ablated_metrics[key] - baseline_metrics[key]) / abs(baseline_metrics[key])
            if baseline_metrics[key] != 0
            else float("nan")
        )
        for key in keys
    }
    return AblationResult(
        experiment=experiment,
        included_groups=included_groups,
        excluded_groups=excluded_groups,
        feature_count=feature_count,
        baseline_metrics=baseline_metrics,
        ablated_metrics=ablated_metrics,
        absolute_change=absolute,
        relative_change=relative,
        observations=observations,
        notes=notes,
    )
