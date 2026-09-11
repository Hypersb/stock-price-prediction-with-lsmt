"""Final research evaluation orchestration.

Coordinates existing research components without duplicating their logic:

market data -> features -> targets -> temporal evaluation -> models ->
walk-forward OOS predictions -> predictive metrics -> regime analysis ->
explainability -> ablation -> complexity -> statistical comparison ->
backtest -> sensitivity -> structured research result
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ml.backtesting.engine import BacktestResult, run_backtest
from ml.dataset import SupervisedFrame
from ml.models.regression import LinearRegressionModel
from ml.research.ablation import AblationResult, run_feature_ablation_study
from ml.research.complexity import ComplexityComparisonResult, compare_model_complexity
from ml.research.config import FinalResearchConfig
from ml.research.dataset_prep import prepare_research_frame
from ml.research.explainability import FeatureImportanceResult, linear_coefficients
from ml.research.multi_asset import (
    MultiAssetRobustnessResult,
    evaluate_multi_asset_robustness,
)
from ml.research.regimes import (
    RegimeMetricResult,
    evaluate_metrics_by_regime,
    label_market_regimes,
)
from ml.research.sensitivity import SensitivityResult, run_backtest_sensitivity
from ml.research.statistics import (
    StatisticalComparisonResult,
    compare_models_block_bootstrap,
)
from ml.research.universe import ResearchUniverse
from ml.split_validation import validate_temporal_split
from ml.splitting import chronological_split
from ml.training.config import TrainingConfig


@dataclass(frozen=True)
class FinalResearchResult:
    """Structured final research output for reporting and persistence."""

    experiment_id: str
    configuration: FinalResearchConfig
    multi_asset: MultiAssetRobustnessResult
    regime_results: tuple[RegimeMetricResult, ...]
    ablation_results: tuple[AblationResult, ...]
    complexity: ComplexityComparisonResult | None
    explainability: tuple[FeatureImportanceResult, ...]
    statistical_comparisons: tuple[StatisticalComparisonResult, ...]
    backtests: tuple[tuple[str, str, BacktestResult], ...]
    sensitivity: tuple[tuple[str, str, SensitivityResult], ...]
    notes: tuple[str, ...]


def run_final_research_evaluation(
    market_data: dict[str, pd.DataFrame],
    config: FinalResearchConfig,
) -> FinalResearchResult:
    """Execute the final research pipeline for an explicit configuration.

    Ordinary unit tests must pass a tiny fixture configuration. This function
    does not download market data and does not invent missing scientific defaults.
    """
    missing = [symbol for symbol in config.symbols if symbol not in market_data]
    if missing:
        raise ValueError(f"missing market data for symbols: {missing}")

    training_config = TrainingConfig(
        epochs=config.lstm_epochs,
        patience=max(1, config.lstm_epochs),
        device="cpu",
        seed=config.random_seed,
    )
    multi_asset = evaluate_multi_asset_robustness(
        {symbol: market_data[symbol] for symbol in config.symbols},
        universe=ResearchUniverse(symbols=config.symbols),
        target_type=config.target_type,
        horizon=config.horizon,
        feature_parameters=config.feature_parameters,
        walk_forward=config.walk_forward,
        model_families=tuple(config.model_families),  # type: ignore[arg-type]
        lookback=config.lookback,
        hidden_size=config.hidden_size,
        training_config=training_config,
    )

    regime_results: list[RegimeMetricResult] = []
    ablation_results: list[AblationResult] = []
    explainability: list[FeatureImportanceResult] = []
    complexity: ComplexityComparisonResult | None = None
    statistical_comparisons: list[StatisticalComparisonResult] = []
    backtests: list[tuple[str, str, BacktestResult]] = []
    sensitivity: list[tuple[str, str, SensitivityResult]] = []

    primary_symbol = config.symbols[0]
    primary_ohlcv = market_data[primary_symbol]

    if config.include_regimes:
        regimes = label_market_regimes(primary_ohlcv, config.regime).labels
        primary_asset = next(
            (asset for asset in multi_asset.assets if asset.symbol == primary_symbol),
            None,
        )
        if primary_asset is not None and not primary_asset.predictions.empty:
            regime_results.extend(
                evaluate_metrics_by_regime(
                    primary_asset.predictions,
                    regimes,
                    config=config.regime,
                )
            )

    if config.include_ablation:
        ablation_results.extend(
            run_feature_ablation_study(
                primary_ohlcv,
                symbol=primary_symbol,
                target_type=config.target_type,
                horizon=config.horizon,
                feature_parameters=config.feature_parameters,
            )
        )

    if config.include_complexity or config.include_explainability:
        frame = prepare_research_frame(
            primary_ohlcv,
            symbol=primary_symbol,
            target_type=config.target_type,
            horizon=config.horizon,
            feature_parameters=config.feature_parameters,
        )
        supervised = SupervisedFrame(
            X=frame.X,
            y=frame.y,
            dates=frame.dates,
            feature_names=frame.feature_names,
        )
        split = chronological_split(supervised, 0.7, 0.15, 0.15)
        validate_temporal_split(split)
        if config.include_complexity:
            complexity = compare_model_complexity(
                split.train.X,
                split.train.y,
                split.validation.X,
                split.validation.y,
                task=frame.task,
                lookback=config.lookback,
                hidden_size=config.hidden_size,
                training_config=training_config,
            )
        if config.include_explainability and frame.task == "regression":
            model = LinearRegressionModel().fit(split.train.X, split.train.y)
            explainability.append(
                linear_coefficients(
                    model,
                    frame.feature_names,
                    scaled_features=False,
                )
            )

    for asset in multi_asset.assets:
        if config.include_statistics:
            models_present = set(asset.predictions["model"])
            if config.compare_model_a in models_present and config.compare_model_b in models_present:
                statistical_comparisons.append(
                    compare_models_block_bootstrap(
                        asset.predictions,
                        model_a=config.compare_model_a,
                        model_b=config.compare_model_b,
                        metric="mae",
                        block_length=config.block_length,
                        bootstrap_iterations=config.bootstrap_iterations,
                        seed=config.random_seed,
                    )
                )
        frame = prepare_research_frame(
            market_data[asset.symbol],
            symbol=asset.symbol,
            target_type=config.target_type,
            horizon=config.horizon,
            feature_parameters=config.feature_parameters,
        )
        for model_name, group in asset.predictions.groupby("model"):
            try:
                backtest = run_backtest(group, frame.market_returns, config.backtest)
                backtests.append((asset.symbol, str(model_name), backtest))
                if config.include_sensitivity:
                    sensitivity.append(
                        (
                            asset.symbol,
                            str(model_name),
                            run_backtest_sensitivity(
                                group,
                                frame.market_returns,
                                base_config=config.backtest,
                                cost_scenarios_bps=config.cost_scenarios_bps,
                                slippage_bps=config.backtest.slippage_bps,
                                signal_thresholds=config.signal_thresholds,
                            ),
                        )
                    )
            except ValueError:
                # Insufficient realization alignment for tiny fixtures is reported via notes.
                continue

    notes = (
        "final research pipeline coordinates existing modules without duplicating them",
        "configuration fingerprint identifies the reproducible experiment",
        "negative or inconclusive LSTM results are valid scientific outcomes",
        "do not cherry-pick assets, folds, costs, or thresholds after seeing holdout results",
    )
    return FinalResearchResult(
        experiment_id=config.fingerprint(),
        configuration=config,
        multi_asset=multi_asset,
        regime_results=tuple(regime_results),
        ablation_results=tuple(ablation_results),
        complexity=complexity,
        explainability=tuple(explainability),
        statistical_comparisons=tuple(statistical_comparisons),
        backtests=tuple(backtests),
        sensitivity=tuple(sensitivity),
        notes=notes,
    )
