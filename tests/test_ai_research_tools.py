"""Tests for evidence-grounded AI research tools and safety."""

from __future__ import annotations

from ml.ai import (
    sanitize_response,
    summarize_backtest_evidence,
    summarize_experiment_evidence,
    summarize_metric_evidence,
)


def test_metric_tool_requires_evidence() -> None:
    assert summarize_metric_evidence({})["status"] == "insufficient_evidence"
    ok = summarize_metric_evidence({"metrics": {"mae": 0.1, "rmse": 0.2}})
    assert ok["status"] == "ok"
    assert ok["metrics"]["mae"] == 0.1


def test_experiment_and_backtest_tools() -> None:
    assert summarize_experiment_evidence({"metrics": {}})["status"] == (
        "insufficient_evidence"
    )
    exp = summarize_experiment_evidence(
        {"experiment_id": "exp-1", "metrics": {"sharpe": 0.5}}
    )
    assert exp["status"] == "ok"
    assert exp["experiment_id"] == "exp-1"

    assert summarize_backtest_evidence({"backtest_id": "b1"})["status"] == (
        "insufficient_evidence"
    )
    bt = summarize_backtest_evidence(
        {
            "backtest_id": "b1",
            "symbol": "aapl",
            "metrics": {"total_return": 0.12},
        }
    )
    assert bt["symbol"] == "AAPL"
    assert bt["status"] == "ok"


def test_sanitize_refuses_guaranteed_returns() -> None:
    result = sanitize_response("This strategy offers guaranteed returns forever")
    assert result["status"] == "refused"
    assert result["text"] == ""


def test_sanitize_redacts_secret_patterns() -> None:
    result = sanitize_response("Contact support. api_key=sk-live-abcdef123456")
    assert result["status"] == "ok"
    assert "sk-live" not in result["text"]
    assert "[REDACTED]" in result["text"]
