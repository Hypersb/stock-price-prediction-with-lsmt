"""Repository structural health checks for local developers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRS = (
    "backend/app",
    "ml",
    "frontend/app",
    "tests",
    "docs/startup",
    "docs/adr",
    "scripts",
    "alembic",
)

REQUIRED_STARTUP_DOCS = (
    "FEATURE_INVENTORY.md",
    "ML_RESEARCH_AUDIT.md",
    "EMPIRICAL_RESULTS_AUDIT.md",
    "TEST_BASELINE.md",
    "DEPENDENCY_AUDIT.md",
    "PRODUCT_DEFINITION.md",
    "TARGET_ARCHITECTURE.md",
    "DOMAIN_BOUNDARIES.md",
    "DATA_FLOW.md",
    "ARTIFACT_PROVENANCE.md",
    "CONFIGURATION_AUDIT.md",
    "API_FRONTEND_AUDIT.md",
    "PRODUCTION_READINESS.md",
    "TECHNICAL_DEBT.md",
    "ROADMAP.md",
    "PHASE_1_TRACKER.md",
    "REPOSITORY_STRUCTURE.md",
    "ENTRY_POINTS.md",
    "DEVELOPER_WORKFLOW.md",
    "CONFIGURATION_ARCHITECTURE.md",
    "CONFIGURATION_CONTRACT.md",
    "DOMAIN_DEPENDENCY_MAP.md",
    "INTERNAL_CONTRACTS.md",
)

REQUIRED_ENTRY_POINTS = (
    "backend/app/main.py",
    "backend/app/core/config.py",
    "scripts/docker_backend_entrypoint.py",
    "scripts/fetch_market_data.py",
    "scripts/check_repo_health.py",
    "scripts/print_config.py",
    "alembic.ini",
    "frontend/package.json",
    "docker-compose.yml",
    ".env.example",
)

FORBIDDEN_TRACKED_GLOBS = (
    ".env",
    "frontend/.env.local",
)


def _git_tracked(path: Path) -> bool:
    """Return True when git ls-files lists the path (best-effort)."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def run_checks(repo_root: Path | None = None) -> list[str]:
    """Return a list of human-readable problems (empty means healthy)."""
    root = repo_root or REPO_ROOT
    problems: list[str] = []

    for relative in REQUIRED_DIRS:
        if not (root / relative).is_dir():
            problems.append(f"missing directory: {relative}")

    startup = root / "docs" / "startup"
    for name in REQUIRED_STARTUP_DOCS:
        if not (startup / name).is_file():
            problems.append(f"missing startup doc: docs/startup/{name}")

    for relative in REQUIRED_ENTRY_POINTS:
        if not (root / relative).is_file():
            problems.append(f"missing entry point: {relative}")

    package_json = root / "frontend" / "package.json"
    if package_json.is_file():
        data = json.loads(package_json.read_text(encoding="utf-8"))
        engines = data.get("engines") or {}
        node = str(engines.get("node", ""))
        if "20" not in node:
            problems.append(
                "frontend/package.json engines.node must require Node 20+"
            )
    nvmrc = root / "frontend" / ".nvmrc"
    if not nvmrc.is_file():
        problems.append("missing frontend/.nvmrc")

    docker_reqs = root / "requirements-docker.txt"
    if docker_reqs.is_file():
        text = docker_reqs.read_text(encoding="utf-8")
        if "pandas~=" not in text or "fastapi~=" not in text:
            problems.append(
                "requirements-docker.txt should use pinned compatible ranges"
            )

    for relative in FORBIDDEN_TRACKED_GLOBS:
        path = root / relative
        if path.exists() and _git_tracked(path):
            problems.append(f"secret/env file must not be tracked: {relative}")

    for generated in (
        root / ".pytest_cache",
        root / "frontend" / ".next",
        root / "frontend" / "node_modules",
    ):
        # Existence is fine; tracking is not. Best-effort git check for cache dirs.
        if generated.is_dir() and _git_tracked(generated):
            problems.append(f"generated path must not be tracked: {generated.relative_to(root)}")

    return problems


def main() -> int:
    problems = run_checks()
    if problems:
        print("repository health check FAILED", file=sys.stderr)
        for problem in problems:
            print(f" - {problem}", file=sys.stderr)
        return 1
    print("repository health check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
