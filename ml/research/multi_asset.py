"""Comparable multi-asset walk-forward robustness evaluation."""

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from ml.research.dataset_prep import ResearchFrame, prepare_research_frame
from ml.research.universe import DEFAULT_RESEARCH_UNIVERSE, ResearchUniverse
from ml.training.config import TrainingConfig
from ml.validation.baselines import (
    WalkForwardModelResult,
    evaluate_baselines_walk_forward,
)
from ml.validation.config import WalkForwardConfig
from ml.validation.folds import generate_expanding_folds, generate_rolling_folds
from ml.validation.lstm import evaluate_lstm_walk_forward
from ml.validation.predictions import collect_predictions

ModelFamily = Literal["naive", "linear", "tree", "boosting", "lstm"]


@dataclass(frozen=True)
class ModelAssetSummary:
    """Per-asset aggregate metrics for one model family; never cross-asset blended."""

    model_name: str
    folds: int
    observations: int
    mean_metrics: dict[str, float]
    std_metrics: dict[str, float]
    fold_metrics: tuple[dict[str, float], ...]


@dataclass(frozen=True)
class AssetRobustnessResult:
    """Full structured evaluation for a single asset."""

    symbol: str
    task: str
    horizon: int
    observations: int
    feature_count: int
    model_summaries: tuple[ModelAssetSummary, ...]
    predictions: pd.DataFrame
    fold_results: tuple[WalkForwardModelResult, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class MultiAssetRobustnessResult:
    """Per-asset results preserved separately so weak assets are never hidden."""

    universe: tuple[str, ...]
    task: str
    horizon: int
    walk_forward: WalkForwardConfig
    assets: tuple[AssetRobustnessResult, ...]
    skipped_symbols: tuple[tuple[str, str], ...]

    def summary_table(self) -> pd.DataFrame:
        """One row per symbol/model with mean primary metrics (no pooled blend)."""
        rows: list[dict[str, object]] = []
        for asset in self.assets:
            for summary in asset.model_summaries:
                row: dict[str, object] = {
                    "symbol": asset.symbol,
                    "model": summary.model_name,
                    "folds": summary.folds,
                    "observations": summary.observations,
                }
                row.update({f"mean_{key}": value for key, value in summary.mean_metrics.items()})
                rows.append(row)
        return pd.DataFrame(rows)


def evaluate_multi_asset_robustness(
    market_data: dict[str, pd.DataFrame],
    *,
    universe: ResearchUniverse | None = None,
    target_type: str = "regression",
    horizon: int = 1,
    feature_parameters: dict[str, object] | None = None,
    walk_forward: WalkForwardConfig | None = None,
    model_families: tuple[ModelFamily, ...] = ("naive", "linear", "tree", "lstm"),
    lookback: int = 5,
    hidden_size: int = 8,
    training_config: TrainingConfig | None = None,
    include_lstm: bool | None = None,
) -> MultiAssetRobustnessResult:
    """Evaluate selected model families independently on each configured asset.

    Each asset uses the same target definition, horizon, feature parameters, and
    walk-forward configuration. Results are reported per symbol; there is no
    cross-asset average that could mask underperformance.
    """
    selected_universe = universe or ResearchUniverse(symbols=DEFAULT_RESEARCH_UNIVERSE)
    config = walk_forward or WalkForwardConfig(
        initial_train_size=40,
        validation_size=10,
        test_size=10,
        step_size=10,
        forecast_horizon=horizon,
    )
    families = _resolve_families(model_families, include_lstm)
    assets: list[AssetRobustnessResult] = []
    skipped: list[tuple[str, str]] = []
    task = "regression" if target_type == "regression" else "classification"

    for symbol in selected_universe.symbols:
        frame_data = market_data.get(symbol)
        if frame_data is None:
            frame_data = market_data.get(symbol.upper())
        if frame_data is None:
            skipped.append((symbol, "missing market data"))
            continue
        try:
            frame = prepare_research_frame(
                frame_data,
                symbol=symbol,
                target_type=target_type,
                horizon=horizon,
                feature_parameters=feature_parameters,
            )
            asset_result = evaluate_single_asset_robustness(
                frame,
                walk_forward=config,
                model_families=families,
                lookback=lookback,
                hidden_size=hidden_size,
                training_config=training_config,
            )
            assets.append(asset_result)
        except ValueError as error:
            skipped.append((symbol, str(error)))

    return MultiAssetRobustnessResult(
        universe=selected_universe.symbols,
        task=task,
        horizon=horizon,
        walk_forward=config,
        assets=tuple(assets),
        skipped_symbols=tuple(skipped),
    )


def evaluate_single_asset_robustness(
    frame: ResearchFrame,
    *,
    walk_forward: WalkForwardConfig,
    model_families: tuple[ModelFamily, ...] = ("naive", "linear", "tree", "lstm"),
    lookback: int = 5,
    hidden_size: int = 8,
    training_config: TrainingConfig | None = None,
) -> AssetRobustnessResult:
    """Run comparable walk-forward evaluation for one prepared research frame."""
    n_rows = len(frame.X)
    folds = _generate_folds(n_rows, walk_forward)
    if not folds:
        raise ValueError(f"{frame.symbol}: insufficient rows for walk-forward folds")

    fold_results = _run_selected_models(
        frame,
        folds,
        walk_forward,
        model_families=model_families,
        lookback=lookback,
        hidden_size=hidden_size,
        training_config=training_config,
    )
    summaries = _summarize_by_model(fold_results)
    predictions = collect_predictions(list(fold_results))
    notes: list[str] = []
    if walk_forward.forecast_horizon != frame.horizon:
        notes.append(
            "walk-forward forecast_horizon differs from target horizon; "
            "purging uses walk-forward.forecast_horizon"
        )
    return AssetRobustnessResult(
        symbol=frame.symbol,
        task=frame.task,
        horizon=frame.horizon,
        observations=n_rows,
        feature_count=len(frame.feature_names),
        model_summaries=summaries,
        predictions=predictions,
        fold_results=tuple(fold_results),
        notes=tuple(notes),
    )


def _resolve_families(
    model_families: tuple[ModelFamily, ...],
    include_lstm: bool | None,
) -> tuple[ModelFamily, ...]:
    families = list(model_families)
    if include_lstm is True and "lstm" not in families:
        families.append("lstm")
    if include_lstm is False:
        families = [family for family in families if family != "lstm"]
    if not families:
        raise ValueError("model_families must not be empty")
    return tuple(families)


def _generate_folds(n_rows: int, config: WalkForwardConfig):
    if config.window_type == "expanding":
        return generate_expanding_folds(n_rows, config)
    return generate_rolling_folds(n_rows, config)


def _run_selected_models(
    frame: ResearchFrame,
    folds,
    config: WalkForwardConfig,
    *,
    model_families: tuple[ModelFamily, ...],
    lookback: int,
    hidden_size: int,
    training_config: TrainingConfig | None,
) -> list[WalkForwardModelResult]:
    baseline_wanted = any(family in model_families for family in ("naive", "linear", "tree", "boosting"))
    results: list[WalkForwardModelResult] = []
    if baseline_wanted:
        all_baselines = evaluate_baselines_walk_forward(
            frame.X,
            frame.y,
            frame.dates,
            folds,
            task=frame.task,
            config=config,
        )
        allowed = _baseline_names_for_families(model_families, frame.task)
        results.extend(result for result in all_baselines if result.model_name in allowed)
    if "lstm" in model_families:
        results.extend(
            evaluate_lstm_walk_forward(
                frame.X,
                frame.y,
                frame.dates,
                folds,
                task=frame.task,
                config=config,
                lookback=lookback,
                hidden_size=hidden_size,
                training_config=training_config
                or TrainingConfig(epochs=1, patience=1, device="cpu", seed=42),
            )
        )
    return results


def _baseline_names_for_families(
    model_families: tuple[ModelFamily, ...],
    task: str,
) -> set[str]:
    names: set[str] = set()
    if task == "regression":
        mapping = {
            "naive": "naive_regression",
            "linear": "linear_regression",
            "tree": "random_forest_regression",
            "boosting": "gradient_boosting_regression",
        }
    else:
        mapping = {
            "naive": "naive_direction",
            "linear": "logistic_regression",
            "tree": "random_forest_classifier",
            "boosting": "gradient_boosting_classifier",
        }
    for family in model_families:
        if family in mapping:
            names.add(mapping[family])
    return names


def _summarize_by_model(results: list[WalkForwardModelResult]) -> tuple[ModelAssetSummary, ...]:
    by_model: dict[str, list[WalkForwardModelResult]] = {}
    for result in results:
        by_model.setdefault(result.model_name, []).append(result)
    summaries: list[ModelAssetSummary] = []
    for model_name, model_results in sorted(by_model.items()):
        numeric_folds: list[dict[str, float]] = []
        for result in model_results:
            numeric_folds.append(
                {
                    key: float(value)
                    for key, value in result.metrics.items()
                    if isinstance(value, (int, float, np.floating)) and not isinstance(value, bool)
                }
            )
        keys = sorted({key for fold in numeric_folds for key in fold})
        mean_metrics = {
            key: float(np.mean([fold[key] for fold in numeric_folds if key in fold]))
            for key in keys
        }
        std_metrics = {
            key: float(np.std([fold[key] for fold in numeric_folds if key in fold], ddof=0))
            for key in keys
        }
        summaries.append(
            ModelAssetSummary(
                model_name=model_name,
                folds=len(model_results),
                observations=int(sum(len(result.actual) for result in model_results)),
                mean_metrics=mean_metrics,
                std_metrics=std_metrics,
                fold_metrics=tuple(numeric_folds),
            )
        )
    return tuple(summaries)
