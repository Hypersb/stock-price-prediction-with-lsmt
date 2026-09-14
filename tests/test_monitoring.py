"""Tests for monitoring drift and performance stubs."""

from __future__ import annotations

import numpy as np
import pytest

from ml.monitoring import (
    kolmogorov_smirnov,
    population_stability_index,
    rolling_error_metrics,
)


def test_psi_flags_when_distributions_diverge() -> None:
    rng = np.random.default_rng(0)
    expected = rng.normal(0.0, 1.0, size=500)
    actual = rng.normal(2.0, 1.0, size=500)
    report = population_stability_index(expected, actual, threshold=0.1)
    assert report.method == "psi"
    assert report.score >= 0
    assert report.flagged is True


def test_psi_rejects_empty_inputs() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        population_stability_index([], [1.0, 2.0])


def test_ks_identical_samples_not_flagged() -> None:
    values = [0.1, 0.2, 0.3, 0.4, 0.5]
    report = kolmogorov_smirnov(values, values, threshold=0.05)
    assert report.method == "ks"
    assert report.score == 0.0
    assert report.flagged is False


def test_rolling_errors_insufficient_data() -> None:
    report = rolling_error_metrics([0.1, 0.2], [0.0, 0.1], window=5)
    assert report.status == "insufficient_data"
    assert report.mae is None
    assert report.rmse is None


def test_rolling_errors_ok_with_enough_pairs() -> None:
    preds = list(range(10))
    actuals = [x - 1 for x in preds]
    report = rolling_error_metrics(preds, actuals, window=5)
    assert report.status == "ok"
    assert report.mae == pytest.approx(1.0)
    assert report.rmse == pytest.approx(1.0)
