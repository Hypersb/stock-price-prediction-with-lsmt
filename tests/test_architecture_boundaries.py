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
        "ml.data.symbols",
        "ml.features.pipeline",
        "ml.preprocessing",
    ):
        importlib.import_module(module_name)


def test_backend_main_entrypoint_imports() -> None:
    from backend.app.main import app, create_app

    assert app is not None
    assert create_app is not None
