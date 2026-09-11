"""PostgreSQL migration smoke test for CI services."""

from __future__ import annotations

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from backend.app.db.base import Base
from backend.app.db.session import build_database


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL", "").startswith("postgresql"),
    reason="postgresql DATABASE_URL required",
)
def test_alembic_upgrade_head_on_postgresql() -> None:
    config = Config("alembic.ini")
    command.upgrade(config, "head")

    database = build_database(os.environ["DATABASE_URL"])
    try:
        with database.engine.connect() as connection:
            reflected = set(inspect(connection).get_table_names())
            version = connection.execute(text("select version_num from alembic_version")).scalar()
        assert "alembic_version" in reflected
        assert set(Base.metadata.tables).issubset(reflected)
        assert version
    finally:
        database.engine.dispose()
