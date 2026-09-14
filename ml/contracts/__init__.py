"""Typed research contracts for domain boundaries.

These contracts document and lightly enforce shapes at meaningful boundaries.
They do not replace existing pandas DataFrames used throughout the engine.
"""

from ml.contracts.artifacts import ArtifactKind, ArtifactRef
from ml.contracts.backtesting import (
    SUPPORTED_BACKTEST_HORIZON,
    assert_supported_backtest_horizon,
)
from ml.contracts.dataset import DatasetSpec
from ml.contracts.evaluation import CLASSIFICATION_METRIC_NAMES, REGRESSION_METRIC_NAMES
from ml.contracts.experiments import ExperimentSpec
from ml.contracts.features import FeatureSetSpec
from ml.contracts.market_data import (
    ADJUSTMENT_POLICY_ADJUSTED,
    ADJUSTMENT_POLICY_UNADJUSTED,
    MARKET_DATA_SCHEMA_VERSION,
    OHLCV_OPTIONAL_COLUMNS,
    OHLCV_REQUIRED_COLUMNS,
    MarketDataSemantics,
)
from ml.contracts.models import Predictor
from ml.contracts.predictions import PredictionRecord
from ml.contracts.targets import TargetSpec

__all__ = [
    "ADJUSTMENT_POLICY_ADJUSTED",
    "ADJUSTMENT_POLICY_UNADJUSTED",
    "CLASSIFICATION_METRIC_NAMES",
    "MARKET_DATA_SCHEMA_VERSION",
    "OHLCV_OPTIONAL_COLUMNS",
    "OHLCV_REQUIRED_COLUMNS",
    "REGRESSION_METRIC_NAMES",
    "SUPPORTED_BACKTEST_HORIZON",
    "ArtifactKind",
    "ArtifactRef",
    "DatasetSpec",
    "ExperimentSpec",
    "FeatureSetSpec",
    "MarketDataSemantics",
    "PredictionRecord",
    "Predictor",
    "TargetSpec",
    "assert_supported_backtest_horizon",
]
