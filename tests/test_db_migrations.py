from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from backend.app.db.base import Base
from backend.app.db import models  # noqa: F401
from backend.app.db.session import build_database


def test_alembic_script_directory_contains_initial_revision() -> None:
    config = Config("alembic.ini")
    scripts = ScriptDirectory.from_config(config)
    revisions = list(scripts.walk_revisions())
    assert revisions
    assert any("initial research persistence schema" in item.doc for item in revisions)


def test_metadata_tables_match_expected_research_schema() -> None:
    expected = {
        "experiments",
        "experiment_metrics",
        "walk_forward_runs",
        "walk_forward_folds",
        "out_of_sample_predictions",
        "backtest_runs",
        "backtest_metrics",
        "backtest_equity_points",
    }
    assert expected.issubset(set(Base.metadata.tables))


def test_alembic_upgrade_head_on_isolated_sqlite(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "migration_test.db"
    url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)

    from alembic import command

    config = Config("alembic.ini")
    command.upgrade(config, "head")

    database = build_database(url)
    table_names = set(Base.metadata.tables)
    with database.engine.connect() as connection:
        from sqlalchemy import inspect

        reflected = set(inspect(connection).get_table_names())
    database.engine.dispose()

    assert "alembic_version" in reflected
    assert table_names.issubset(reflected)
