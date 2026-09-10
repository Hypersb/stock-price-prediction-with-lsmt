"""Numerical technical indicators without trading signals."""

import pandas as pd


def relative_strength_index(close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Wilder-style RSI using recursive alpha ``1 / period`` smoothing."""
    _validate_series(close, "close")
    _validate_period(period)
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    average_gain = gains.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    average_loss = losses.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    relative_strength = average_gain / average_loss
    return (100 - 100 / (1 + relative_strength)).rename(f"rsi_{period}")


def macd_features(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """Calculate adjust=False MACD, signal, and histogram columns."""
    _validate_series(close, "close")
    _validate_period(fast)
    _validate_period(slow)
    _validate_period(signal)
    if fast >= slow:
        raise ValueError("fast period must be smaller than slow period")
    fast_ema = close.ewm(span=fast, adjust=False, min_periods=fast).mean()
    slow_ema = close.ewm(span=slow, adjust=False, min_periods=slow).mean()
    macd = (fast_ema - slow_ema).rename("macd")
    macd_signal = macd.ewm(span=signal, adjust=False, min_periods=signal).mean().rename("macd_signal")
    return pd.DataFrame(
        {"macd": macd, "macd_signal": macd_signal, "macd_histogram": macd - macd_signal},
        index=close.index,
    )


def average_true_range(
    data: pd.DataFrame,
    period: int = 14,
) -> pd.Series:
    """Calculate ATR from true range using Wilder alpha ``1 / period`` smoothing."""
    _validate_period(period)
    required = {"high", "low", "close"}
    if not isinstance(data, pd.DataFrame) or not required.issubset(data.columns):
        raise ValueError("data must contain high, low, and close columns")
    high = data["high"]
    low = data["low"]
    close = data["close"]
    if any(series.isna().any() for series in (high, low, close)):
        raise ValueError("high, low, and close values must not be missing")
    previous_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - previous_close).abs(), (low - previous_close).abs()], axis=1
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean().rename(
        f"atr_{period}"
    )


def _validate_series(series: pd.Series, name: str) -> None:
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name} must be a pandas Series")
    if series.isna().any() or (series <= 0).any():
        raise ValueError(f"{name} values must be positive and non-missing")


def _validate_period(period: int) -> None:
    if isinstance(period, bool) or not isinstance(period, int) or period <= 0:
        raise ValueError("period must be a positive integer")