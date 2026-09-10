"""Convert strictly out-of-sample predictions into research signals."""

import pandas as pd

from ml.backtesting.config import BacktestConfig


def prediction_signals(
    predictions: pd.DataFrame,
    config: BacktestConfig,
    *,
    classification_upper: float = 0.5,
    classification_lower: float = 0.5,
) -> pd.DataFrame:
    """Create signals from predictions without consulting realized returns."""
    required = {"date", "model", "task"}
    if not required.issubset(predictions.columns):
        raise ValueError("predictions must contain date, model, and task columns")
    result = predictions.copy()
    if result["date"].isna().any():
        raise ValueError("prediction dates must not be missing")
    if not 0 <= classification_lower <= classification_upper <= 1:
        raise ValueError("classification thresholds must be within [0, 1]")
    signals = []
    for row in result.itertuples(index=False):
        if row.task == "regression":
            if not hasattr(row, "predicted"):
                raise ValueError("regression predictions require predicted values")
            value = row.predicted
            signal = 1 if value > config.signal_threshold else 0
            if config.strategy_mode == "long_short" and value < -config.signal_threshold:
                signal = -1
        elif row.task == "classification":
            if not hasattr(row, "probability"):
                raise ValueError("classification predictions require probability values")
            probability = row.probability
            if not 0 <= probability <= 1:
                raise ValueError("classification probabilities must be within [0, 1]")
            signal = 1 if probability >= classification_upper else 0
            if config.strategy_mode == "long_short" and probability <= classification_lower:
                signal = -1
        else:
            raise ValueError("prediction task must be regression or classification")
        signals.append(signal)
    result["signal"] = signals
    return result