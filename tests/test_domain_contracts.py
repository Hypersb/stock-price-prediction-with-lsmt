"""Contract tests for domain boundary types (no methodology changes)."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from ml.backtesting.execution import align_execution
from ml.contracts import (
    ADJUSTMENT_POLICY_UNADJUSTED,
    OHLCV_REQUIRED_COLUMNS,
    ArtifactRef,
    DatasetSpec,
    ExperimentSpec,
    FeatureSetSpec,
    MarketDataSemantics,
    PredictionRecord,
    Predictor,
    TargetSpec,
    assert_supported_backtest_horizon,
)
from ml.errors import BacktestError, DataValidationError
from ml.models.baselines import NaiveRegression
from ml.targets.returns import future_return_targets


def test_market_data_semantics_match_schema() -> None:
    semantics = MarketDataSemantics()
    assert semantics.required_columns == OHLCV_REQUIRED_COLUMNS
    assert semantics.adjustment_policy == ADJUSTMENT_POLICY_UNADJUSTED
    semantics.assert_columns(OHLCV_REQUIRED_COLUMNS)


def test_dataset_spec_rejects_inverted_range() -> None:
    with pytest.raises(ValueError, match="start_date"):
        DatasetSpec(
            dataset_id="ds1",
            symbol="AAPL",
            provider="yahoo",
            start_date=date(2024, 1, 1),
            end_date=date(2023, 1, 1),
        )


def test_feature_set_rejects_target_like_names() -> None:
    with pytest.raises(ValueError, match="forbidden"):
        FeatureSetSpec(
            feature_set_id="f1",
            feature_names=("momentum_5", "future_return"),
            lookback_bars=5,
        )


def test_target_spec_future_return_naming() -> None:
    spec = TargetSpec.future_return(1)
    assert spec.column_name == "future_return_1"
    close = pd.Series([100.0, 110.0, 121.0])
    targets = future_return_targets(close, [1])
    assert spec.column_name in targets.columns


def test_naive_regression_satisfies_predictor_protocol() -> None:
    model = NaiveRegression()
    assert isinstance(model, Predictor)
    X = pd.DataFrame({"a": [1.0, 2.0]})
    y = pd.Series([0.0, 0.0])
    model.fit(X, y)
    preds = model.predict(X)
    assert len(preds) == 2


def test_prediction_record_requires_model_name() -> None:
    with pytest.raises(ValueError, match="model_name"):
        PredictionRecord(
            symbol="AAPL",
            model_name=" ",
            prediction_date=date(2020, 1, 2),
            target_date=date(2020, 1, 3),
            horizon=1,
            predicted=0.01,
        )


def test_backtest_horizon_contract_fail_loud() -> None:
    with pytest.raises(BacktestError, match="forecast_horizon"):
        assert_supported_backtest_horizon(5)
    signals = pd.DataFrame({"date": pd.to_datetime(["2020-01-01"]), "signal": [1]})
    returns = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "realized_return": [0.0, 0.1],
        }
    )
    with pytest.raises(BacktestError, match="forecast_horizon"):
        align_execution(signals, returns, forecast_horizon=2)


def test_experiment_and_artifact_contracts() -> None:
    experiment = ExperimentSpec(experiment_id="exp-1", model_name="lstm", random_seed=7)
    artifact = ArtifactRef(
        artifact_id="art-1",
        kind="predictions",
        path="artifacts/exp-1/preds.csv",
        experiment_id=experiment.experiment_id,
    )
    assert artifact.kind == "predictions"


def test_market_data_validation_error_is_domain_error() -> None:
    from ml.data.validation import MarketDataValidationError

    assert issubclass(MarketDataValidationError, DataValidationError)
    assert issubclass(MarketDataValidationError, ValueError)
