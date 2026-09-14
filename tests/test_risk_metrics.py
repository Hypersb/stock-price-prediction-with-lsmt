"""Tests for historical risk analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ml.risk import (
    beta,
    calmar_ratio,
    historical_expected_shortfall,
    historical_var,
    summarize_return_risk,
    tracking_error,
)


def test_historical_var_and_es_are_nonnegative() -> None:
    rng = np.random.default_rng(0)
    returns = pd.Series(rng.normal(0.0, 0.01, size=500))
    var = historical_var(returns, confidence=0.95)
    es = historical_expected_shortfall(returns, confidence=0.95)
    assert var >= 0
    assert es >= var


def test_summarize_return_risk_includes_calmar() -> None:
    returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.005] * 40)
    summary = summarize_return_risk(returns, var_confidence=0.9)
    assert summary.calmar_ratio == calmar_ratio(
        summary.annualized_return, summary.maximum_drawdown
    )
    assert summary.var_confidence == 0.9


def test_beta_and_tracking_error() -> None:
    bench = pd.Series(np.linspace(-0.01, 0.01, 100))
    asset = bench * 1.5 + 0.0001
    assert abs(beta(asset, bench) - 1.5) < 1e-6
    assert tracking_error(asset, bench) >= 0


def test_var_rejects_bad_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        historical_var(pd.Series([0.01, -0.01]), confidence=1.0)
