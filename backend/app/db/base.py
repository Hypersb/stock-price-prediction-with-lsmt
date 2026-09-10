"""SQLAlchemy declarative base for research persistence."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for ORM models."""
