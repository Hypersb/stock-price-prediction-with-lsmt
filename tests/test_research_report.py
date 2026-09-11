"""Tests for research report rendering without fabricated results."""

from ml.research.report import render_final_research_report


def test_report_marks_missing_results_as_awaiting() -> None:
    document = render_final_research_report(None)
    assert document.populated_from_results is False
    assert document.experiment_id is None
    assert "Awaiting generated results" in document.markdown
    assert "does not demonstrate that the LSTM" in document.markdown


def test_report_contains_required_sections() -> None:
    markdown = render_final_research_report(None).markdown
    for section in (
        "Executive Summary",
        "Research Question",
        "Multi-Asset Results",
        "Regime Results",
        "Feature Importance",
        "Ablation Results",
        "Model Complexity",
        "Statistical Comparison",
        "Backtesting Results",
        "Cost Sensitivity",
        "Limitations",
        "Conclusions",
        "Future Work",
    ):
        assert section in markdown
