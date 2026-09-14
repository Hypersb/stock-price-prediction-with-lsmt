"""Quantitative risk analytics for return series and portfolios.

Assumptions are documented per function. Historical risk measures do not
predict future losses. VaR/ES use historical simulation unless noted.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml.backtesting.metrics import calculate_metrics


@dataclass(frozen=True)
class RiskMetrics:
    """Bundle of common risk statistics for a return series."""

    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    maximum_drawdown: float
    calmar_ratio: float
    downside_deviation: float
    hit_rate: float
    var: float
    expected_shortfall: float
    var_confidence: float
    annualization_factor: float


def downside_deviation(
    returns: pd.Series,
    *,
    annualization_factor: float = 252,
    risk_free_rate: float = 0.0,
) -> float:
    """Annualized downside deviation of excess returns (Sortino denominator)."""
    series = pd.Series(returns).dropna().astype(float)
    if series.empty or annualization_factor <= 0:
        raise ValueError("returns must be non-empty and annualization_factor positive")
    daily_rf = (1 + risk_free_rate) ** (1 / annualization_factor) - 1
    downside = (series - daily_rf).clip(upper=0)
    return float(np.sqrt((downside**2).mean()) * math.sqrt(annualization_factor))


def calmar_ratio(annualized_return: float, maximum_drawdown: float) -> float:
    """Calmar = annualized return / |max drawdown|; 0 if drawdown is 0."""
    if maximum_drawdown == 0:
        return 0.0
    return float(annualized_return / abs(maximum_drawdown))


def historical_var(
    returns: pd.Series,
    *,
    confidence: float = 0.95,
) -> float:
    """Historical VaR as a positive loss fraction at the given confidence.

    Example: 0.03 means a 3% loss threshold. Uses the empirical quantile of
    the left tail. Requires ``confidence`` in (0, 1).
    """
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    series = pd.Series(returns).dropna().astype(float)
    if series.empty:
        raise ValueError("returns must be non-empty")
    alpha = 1.0 - confidence
    quantile = float(series.quantile(alpha))
    return float(max(0.0, -quantile))


def historical_expected_shortfall(
    returns: pd.Series,
    *,
    confidence: float = 0.95,
) -> float:
    """Historical Expected Shortfall (CVaR) as a positive average tail loss."""
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    series = pd.Series(returns).dropna().astype(float)
    if series.empty:
        raise ValueError("returns must be non-empty")
    alpha = 1.0 - confidence
    threshold = float(series.quantile(alpha))
    tail = series[series <= threshold]
    if tail.empty:
        return historical_var(series, confidence=confidence)
    return float(max(0.0, -tail.mean()))


def beta(asset_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """OLS beta of asset vs benchmark on aligned dates."""
    asset = pd.Series(asset_returns).astype(float)
    bench = pd.Series(benchmark_returns).astype(float)
    aligned = pd.concat([asset, bench], axis=1, join="inner").dropna()
    if len(aligned) < 2:
        raise ValueError("need at least two overlapping observations for beta")
    cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1], ddof=1)
    var_b = float(cov[1, 1])
    if var_b == 0:
        return 0.0
    return float(cov[0, 1] / var_b)


def tracking_error(
    asset_returns: pd.Series,
    benchmark_returns: pd.Series,
    *,
    annualization_factor: float = 252,
) -> float:
    """Annualized tracking error of active returns."""
    asset = pd.Series(asset_returns).astype(float)
    bench = pd.Series(benchmark_returns).astype(float)
    active = (asset - bench).dropna()
    if len(active) < 2 or annualization_factor <= 0:
        raise ValueError("need variance sample and positive annualization_factor")
    return float(active.std(ddof=1) * math.sqrt(annualization_factor))


def summarize_return_risk(
    returns: pd.Series,
    *,
    annualization_factor: float = 252,
    risk_free_rate: float = 0.0,
    var_confidence: float = 0.95,
) -> RiskMetrics:
    """Compose backtest-compatible metrics plus VaR/ES/Calmar."""
    base = calculate_metrics(
        returns,
        annualization_factor=annualization_factor,
        risk_free_rate=risk_free_rate,
    )
    dd = downside_deviation(
        returns,
        annualization_factor=annualization_factor,
        risk_free_rate=risk_free_rate,
    )
    return RiskMetrics(
        total_return=base["total_return"],
        annualized_return=base["annualized_return"],
        annualized_volatility=base["annualized_volatility"],
        sharpe_ratio=base["sharpe_ratio"],
        sortino_ratio=base["sortino_ratio"],
        maximum_drawdown=base["maximum_drawdown"],
        calmar_ratio=calmar_ratio(base["annualized_return"], base["maximum_drawdown"]),
        downside_deviation=dd,
        hit_rate=base["hit_rate"],
        var=historical_var(returns, confidence=var_confidence),
        expected_shortfall=historical_expected_shortfall(
            returns, confidence=var_confidence
        ),
        var_confidence=var_confidence,
        annualization_factor=annualization_factor,
    )
