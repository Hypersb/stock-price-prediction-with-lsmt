from sqlalchemy import text

from backend.app.core.config import clear_settings_cache
from backend.app.db.session import (
    build_database,
    configure_database,
    get_database,
    get_db_session,
    reset_database,
)


def test_build_database_creates_usable_sqlite_session() -> None:
    database = build_database("sqlite:///:memory:")
    with database.create_session() as session:
        value = session.execute(text("SELECT 1")).scalar_one()
        assert value == 1
    database.engine.dispose()


def test_configure_database_uses_environment_url(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    clear_settings_cache()
    reset_database()

    database = configure_database()
    assert get_database() is database
    with database.create_session() as session:
        assert session.execute(text("SELECT 1")).scalar_one() == 1

    reset_database()


def test_get_db_session_commits_and_closes(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    clear_settings_cache()
    reset_database()
    configure_database()

    generator = get_db_session()
    session = next(generator)
    assert session.execute(text("SELECT 1")).scalar_one() == 1
    try:
        next(generator)
    except StopIteration:
        pass

    reset_database()


def test_configure_database_requires_url(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "")
    clear_settings_cache()
    reset_database()
    try:
        configure_database()
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "DATABASE_URL" in str(exc)
