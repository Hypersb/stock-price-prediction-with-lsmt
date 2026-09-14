"""Quantitative risk analytics for return series.

Historical VaR/ES do not predict future losses. See ``ml.risk.metrics``.
"""

from ml.risk.metrics import (
    RiskMetrics,
    beta,
    calmar_ratio,
    downside_deviation,
    historical_expected_shortfall,
    historical_var,
    summarize_return_risk,
    tracking_error,
)

__all__ = [
    "RiskMetrics",
    "beta",
    "calmar_ratio",
    "downside_deviation",
    "historical_expected_shortfall",
    "historical_var",
    "summarize_return_risk",
    "tracking_error",
]
