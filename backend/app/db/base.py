"""SQLAlchemy declarative base for research persistence."""

from sqlalchemy.orm import DeclarativeBase

from backend.app.db.types import NAMING_METADATA


class Base(DeclarativeBase):
    """Shared declarative base for ORM models."""

    metadata = NAMING_METADATA
