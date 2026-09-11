"""Causal rule-based market regime labels for historical analysis.

Regimes are diagnostic labels, not causal claims. All inputs use trailing
information available at or before each observation. Thresholds are explicit
and configurable; they must not be fit on the full sample in a way that leaks
future information into historical labels.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml.data.validation import validate_ohlcv


@dataclass(frozen=True)
class RegimeConfig:
    """Explicit, documented thresholds for trailing regime classification."""

    trend_ma_window: int = 50
    trend_return_window: int = 20
    bullish_return_threshold: float = 0.0
    bearish_return_threshold: float = 0.0
    volatility_window: int = 20
    volatility_low_quantile: float = 0.33
    volatility_high_quantile: float = 0.67
    # Expanding quantile uses only history up to each row (causal).
    volatility_min_history: int = 60
    min_observations_per_regime: int = 30

    def __post_init__(self) -> None:
        for name in (
            "trend_ma_window",
            "trend_return_window",
            "volatility_window",
            "volatility_min_history",
            "min_observations_per_regime",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.bearish_return_threshold > self.bullish_return_threshold:
            raise ValueError("bearish_return_threshold must be <= bullish_return_threshold")
        if not 0.0 < self.volatility_low_quantile < self.volatility_high_quantile < 1.0:
            raise ValueError("volatility quantiles must satisfy 0 < low < high < 1")


@dataclass(frozen=True)
class RegimeFrame:
    """Per-date causal regime labels aligned to OHLCV chronology."""

    labels: pd.DataFrame
    configuration: RegimeConfig


@dataclass(frozen=True)
class RegimeMetricResult:
    """Model metrics within one regime bucket, gated by minimum counts."""

    dimension: str
    regime: str
    model: str
    observations: int
    interpretable: bool
    metrics: dict[str, float]
    note: str


def label_market_regimes(
    ohlcv: pd.DataFrame,
    config: RegimeConfig | None = None,
) -> RegimeFrame:
    """Assign trend and volatility regimes using only trailing information."""
    validate_ohlcv(ohlcv)
    configuration = config or RegimeConfig()
    frame = ohlcv.reset_index(drop=True).copy()
    close = frame["close"].astype(float)
    dates = pd.to_datetime(frame["date"])
    if not dates.is_monotonic_increasing:
        raise ValueError("regime input dates must be chronological")

    trailing_ma = close.rolling(configuration.trend_ma_window, min_periods=configuration.trend_ma_window).mean()
    trailing_return = close.pct_change(configuration.trend_return_window)
    above_ma = close > trailing_ma
    trend = pd.Series(index=frame.index, dtype=object)
    trend[:] = np.nan
    bullish = above_ma & (trailing_return > configuration.bullish_return_threshold)
    bearish = (~above_ma) & (trailing_return < configuration.bearish_return_threshold)
    neutral_mask = trailing_ma.notna() & trailing_return.notna() & ~(bullish | bearish)
    trend.loc[bullish.fillna(False)] = "bullish"
    trend.loc[bearish.fillna(False)] = "bearish"
    trend.loc[neutral_mask.fillna(False)] = "neutral"

    log_return = np.log(close / close.shift(1))
    realized_vol = log_return.rolling(
        configuration.volatility_window,
        min_periods=configuration.volatility_window,
    ).std()
    low_q, high_q = _expanding_causal_quantiles(
        realized_vol,
        low_quantile=configuration.volatility_low_quantile,
        high_quantile=configuration.volatility_high_quantile,
        min_history=configuration.volatility_min_history,
    )
    volatility = pd.Series(index=frame.index, dtype=object)
    volatility[:] = np.nan
    ready = realized_vol.notna() & low_q.notna() & high_q.notna()
    volatility.loc[ready & (realized_vol <= low_q)] = "low"
    volatility.loc[ready & (realized_vol >= high_q)] = "high"
    volatility.loc[ready & (realized_vol > low_q) & (realized_vol < high_q)] = "normal"

    labels = pd.DataFrame(
        {
            "date": dates,
            "trend_regime": trend,
            "volatility_regime": volatility,
            "trailing_ma": trailing_ma,
            "trailing_return": trailing_return,
            "realized_volatility": realized_vol,
            "vol_low_threshold": low_q,
            "vol_high_threshold": high_q,
        }
    )
    return RegimeFrame(labels=labels, configuration=configuration)


def evaluate_metrics_by_regime(
    predictions: pd.DataFrame,
    regimes: pd.DataFrame,
    *,
    config: RegimeConfig | None = None,
    metric_keys: tuple[str, ...] | None = None,
) -> tuple[RegimeMetricResult, ...]:
    """Aggregate predictive metrics by regime for each model.

    Requires ``config.min_observations_per_regime`` before marking a result
    interpretable. Does not claim causal regime effects.
    """
    configuration = config or RegimeConfig()
    required = {"date", "model", "actual", "predicted"}
    if not required.issubset(predictions.columns):
        raise ValueError(f"predictions must contain columns {sorted(required)}")
    if "date" not in regimes.columns:
        raise ValueError("regimes must contain a date column")
    merged = predictions.copy()
    merged["date"] = pd.to_datetime(merged["date"])
    regime_frame = regimes.copy()
    regime_frame["date"] = pd.to_datetime(regime_frame["date"])
    merged = merged.merge(
        regime_frame[["date", "trend_regime", "volatility_regime"]],
        on="date",
        how="left",
    )
    results: list[RegimeMetricResult] = []
    for dimension, column in (("trend", "trend_regime"), ("volatility", "volatility_regime")):
        for regime_name, group in merged.groupby([column, "model"], dropna=True):
            regime_label, model_name = regime_name
            metrics = _paired_metrics(group["actual"].to_numpy(), group["predicted"].to_numpy())
            if metric_keys is not None:
                metrics = {key: metrics[key] for key in metric_keys if key in metrics}
            observations = len(group)
            interpretable = observations >= configuration.min_observations_per_regime
            note = (
                "minimum observation count met"
                if interpretable
                else (
                    f"insufficient observations ({observations} < "
                    f"{configuration.min_observations_per_regime}); do not interpret"
                )
            )
            results.append(
                RegimeMetricResult(
                    dimension=dimension,
                    regime=str(regime_label),
                    model=str(model_name),
                    observations=observations,
                    interpretable=interpretable,
                    metrics=metrics,
                    note=note,
                )
            )
    return tuple(results)


def _expanding_causal_quantiles(
    series: pd.Series,
    *,
    low_quantile: float,
    high_quantile: float,
    min_history: int,
) -> tuple[pd.Series, pd.Series]:
    """Compute expanding quantiles using only values at or before each index."""
    values = series.to_numpy(dtype=float)
    low = np.full(len(values), np.nan)
    high = np.full(len(values), np.nan)
    history: list[float] = []
    for index, value in enumerate(values):
        if np.isfinite(value):
            history.append(float(value))
        if len(history) < min_history:
            continue
        # Quantiles use history including the current observation (available now).
        low[index] = float(np.quantile(history, low_quantile))
        high[index] = float(np.quantile(history, high_quantile))
    return pd.Series(low, index=series.index), pd.Series(high, index=series.index)


def _paired_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    if len(actual) == 0:
        return {}
    residual = predicted - actual
    mae = float(np.mean(np.abs(residual)))
    rmse = float(np.sqrt(np.mean(residual**2)))
    directional = float(np.mean(np.sign(predicted) == np.sign(actual)))
    return {"mae": mae, "rmse": rmse, "directional_accuracy": directional}
