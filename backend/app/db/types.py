"""Shared ORM column helpers for research persistence."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

# Naming convention keeps Alembic/PostgreSQL constraint names stable.
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

NAMING_METADATA = MetaData(naming_convention=convention)


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def uuid_pk() -> Mapped[uuid.UUID]:
    """UUID primary key column factory."""
    return mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)


def created_at_column() -> Mapped[datetime]:
    """Timezone-aware created_at column."""
    return mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )


def updated_at_column() -> Mapped[datetime]:
    """Timezone-aware updated_at column."""
    return mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
