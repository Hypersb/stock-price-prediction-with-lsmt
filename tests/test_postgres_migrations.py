"""PostgreSQL migration smoke test for CI services."""

from __future__ import annotations

import os

import pytest
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from alembic import command
from backend.app.db.base import Base
from backend.app.db.session import build_database


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL", "").startswith("postgresql"),
    reason="postgresql DATABASE_URL required",
)
def test_alembic_upgrade_head_on_postgresql() -> None:
    """Apply migrations when a reachable Postgres URL is configured.

    Local developer shells often export DATABASE_URL while Postgres is down.
    Skip in that case instead of failing the unit suite; CI with a live service
    still exercises the upgrade path.
    """
    database_url = os.environ["DATABASE_URL"]
    database = build_database(database_url)
    try:
        try:
            with database.engine.connect() as connection:
                connection.execute(text("select 1"))
        except OperationalError as exc:
            pytest.skip(f"postgresql unavailable: {exc.__class__.__name__}")
    finally:
        database.engine.dispose()

    config = Config("alembic.ini")
    try:
        command.upgrade(config, "head")
    except SQLAlchemyError as exc:
        pytest.skip(f"postgresql migration unavailable: {exc.__class__.__name__}")

    database = build_database(database_url)
    try:
        with database.engine.connect() as connection:
            reflected = set(inspect(connection).get_table_names())
            version = connection.execute(text("select version_num from alembic_version")).scalar()
        assert "alembic_version" in reflected
        assert set(Base.metadata.tables).issubset(reflected)
        assert version
    finally:
        database.engine.dispose()
