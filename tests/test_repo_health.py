"""Tests for repository health checks."""

from scripts.check_repo_health import run_checks


def test_repository_health_checks_pass_on_current_tree() -> None:
    assert run_checks() == []
