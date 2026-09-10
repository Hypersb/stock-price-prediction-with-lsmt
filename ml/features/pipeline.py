"""Orchestration for leakage-aware OHLCV feature engineering."""

from collections.abc import Iterable

import pandas as pd

from ml.analysis.returns import log_returns, simple_returns
from ml.data.validation import validate_ohlcv
from ml.features.ema import exponential_moving_average_features
from ml.features.indicators import (
    average_true_range,
    macd_features,
    relative_strength_index,
)
from ml.features.lag import lagged_returns
from ml.features.momentum import momentum_features
from ml.features.trend import moving_average_features
from ml.features.volatility import volatility_features
from ml.features.volume import volume_features


def build_features(
    data: pd.DataFrame,
    *,
    return_lags: Iterable[int] = (1, 2, 3, 5, 10),
    momentum_windows: Iterable[int] = (5, 10, 20, 60),
    moving_average_windows: Iterable[int] = (5, 10, 20, 50, 200),
    ema_spans: Iterable[int] = (12, 26, 50),
    volatility_windows: Iterable[int] = (5, 10, 20, 60),
    volume_window: int = 20,
    rsi_period: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    atr_period: int = 14,
) -> pd.DataFrame:
    """Build deterministic features from validated, chronologically ordered OHLCV."""
    validate_ohlcv(data)
    dates = pd.to_datetime(data["date"])
    if not dates.is_monotonic_increasing:
        raise ValueError("feature input dates must be chronological")
    close = data["close"].reset_index(drop=True)
    returns = simple_returns(pd.DataFrame({"close": close}))
    result = data.reset_index(drop=True).copy()
    result["simple_return"] = returns
    result["log_return"] = log_returns(pd.DataFrame({"close": close}))
    feature_frames = [
        lagged_returns(returns, return_lags),
        momentum_features(close, momentum_windows),
        moving_average_features(close, moving_average_windows),
        exponential_moving_average_features(close, ema_spans),
        volatility_features(close, volatility_windows),
        volume_features(result["volume"], volume_window),
        pd.DataFrame(
            {
                f"rsi_{rsi_period}": relative_strength_index(close, rsi_period),
            }
        ),
        macd_features(close, macd_fast, macd_slow, macd_signal),
        pd.DataFrame({f"atr_{atr_period}": average_true_range(result, atr_period)}),
    ]
    return pd.concat([result, *feature_frames], axis=1)