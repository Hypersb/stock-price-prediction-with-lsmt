"""Architectural boundary invariants for the modular monolith."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _iter_python_files(relative: str):
    root = REPO_ROOT / relative
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_ml_does_not_import_backend_or_frontend() -> None:
    violations: list[str] = []
    for path in _iter_python_files("ml"):
        for module in _imported_modules(path):
            top = module.split(".", 1)[0]
            if top in {"backend", "frontend"}:
                violations.append(f"{path.relative_to(REPO_ROOT)} imports {module}")
    assert violations == []


def test_ml_does_not_import_fastapi() -> None:
    violations: list[str] = []
    for path in _iter_python_files("ml"):
        for module in _imported_modules(path):
            if module == "fastapi" or module.startswith("fastapi."):
                violations.append(f"{path.relative_to(REPO_ROOT)} imports {module}")
    assert violations == []


def test_ml_does_not_import_backend_api_schemas() -> None:
    violations: list[str] = []
    for path in _iter_python_files("ml"):
        for module in _imported_modules(path):
            if module.startswith("backend.app.schemas"):
                violations.append(f"{path.relative_to(REPO_ROOT)} imports {module}")
    assert violations == []


def test_yfinance_is_confined_to_yahoo_adapter() -> None:
    allowed = {
        REPO_ROOT / "ml" / "data" / "yahoo.py",
        REPO_ROOT / "tests" / "test_yahoo_provider.py",
    }
    violations: list[str] = []
    for relative in ("ml", "backend", "scripts"):
        for path in _iter_python_files(relative):
            modules = _imported_modules(path)
            uses_yfinance = "yfinance" in modules or any(
                m.startswith("yfinance.") for m in modules
            )
            if uses_yfinance and path not in allowed:
                violations.append(str(path.relative_to(REPO_ROOT)))
    assert violations == []


def test_api_routes_do_not_import_yfinance_or_yahoo_provider() -> None:
    violations: list[str] = []
    for path in _iter_python_files("backend/app/api"):
        for module in _imported_modules(path):
            if module in {"yfinance", "ml.data.yahoo"} or module.startswith("yfinance."):
                violations.append(f"{path.relative_to(REPO_ROOT)} imports {module}")
    assert violations == []


def test_core_quantitative_modules_import_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Import domain modules without allowing accidental network during import."""
    import importlib

    def _blocked(*_args, **_kwargs):  # pragma: no cover - fail path
        raise AssertionError("network access attempted during domain import")

    monkeypatch.setattr("socket.socket", _blocked)

    for module_name in (
        "ml.analysis.drawdown",
        "ml.analysis.returns",
        "ml.backtesting.metrics",
        "ml.contracts",
        "ml.data.symbols",
        "ml.errors",
        "ml.features.pipeline",
        "ml.preprocessing",
    ):
        importlib.import_module(module_name)


def test_backend_main_entrypoint_imports() -> None:
    from backend.app.main import app, create_app

    assert app is not None
    assert create_app is not None
