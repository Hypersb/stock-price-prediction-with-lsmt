"""Structured research tools that only echo provided evidence.

If required keys are missing, tools return ``{"status": "insufficient_evidence"}``
rather than inventing metrics, news, or users.
"""

from __future__ import annotations

from typing import Any


def _insufficient() -> dict[str, Any]:
    return {"status": "insufficient_evidence"}


def summarize_metric_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Return metric name/value pairs only when present in ``evidence``."""
    if not isinstance(evidence, dict):
        return _insufficient()
    metrics = evidence.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        return _insufficient()
    cleaned: dict[str, float] = {}
    for key, value in metrics.items():
        try:
            cleaned[str(key)] = float(value)
        except (TypeError, ValueError):
            return _insufficient()
    return {
        "status": "ok",
        "metrics": cleaned,
        "source": "provided_evidence",
    }


def summarize_experiment_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Return experiment identifiers and listed metrics from evidence only."""
    if not isinstance(evidence, dict):
        return _insufficient()
    experiment_id = evidence.get("experiment_id")
    if not experiment_id or not str(experiment_id).strip():
        return _insufficient()
    metrics = evidence.get("metrics")
    if metrics is None:
        metrics = {}
    if not isinstance(metrics, dict):
        return _insufficient()
    return {
        "status": "ok",
        "experiment_id": str(experiment_id),
        "metrics": {str(k): float(v) for k, v in metrics.items()},
        "source": "provided_evidence",
    }


def summarize_backtest_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Return backtest summary fields only when present in evidence."""
    if not isinstance(evidence, dict):
        return _insufficient()
    required = ("backtest_id", "symbol", "metrics")
    if any(key not in evidence for key in required):
        return _insufficient()
    metrics = evidence.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        return _insufficient()
    try:
        cleaned = {str(k): float(v) for k, v in metrics.items()}
    except (TypeError, ValueError):
        return _insufficient()
    return {
        "status": "ok",
        "backtest_id": str(evidence["backtest_id"]),
        "symbol": str(evidence["symbol"]).upper(),
        "metrics": cleaned,
        "source": "provided_evidence",
    }
