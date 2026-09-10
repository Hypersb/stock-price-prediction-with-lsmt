"""Database engine and session factory helpers."""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import Settings, get_settings


@dataclass
class Database:
    """Bound engine and session factory for one database URL."""

    engine: Engine
    session_factory: sessionmaker[Session]

    def create_session(self) -> Session:
        """Open a new SQLAlchemy session."""
        return self.session_factory()


_database: Database | None = None


def create_engine_from_url(database_url: str, *, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL or SQLite test URLs."""
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(
        database_url,
        echo=echo,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
    if database_url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_fk(dbapi_connection, connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a session factory bound to the given engine."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


def build_database(database_url: str, *, echo: bool = False) -> Database:
    """Construct an engine/session pair without mutating global state."""
    engine = create_engine_from_url(database_url, echo=echo)
    return Database(engine=engine, session_factory=create_session_factory(engine))


def configure_database(
    database_url: str | None = None,
    *,
    settings: Settings | None = None,
    echo: bool = False,
) -> Database:
    """Configure the process-wide database handle used by FastAPI."""
    global _database
    active = settings or get_settings()
    url = database_url or active.database_url
    if not url:
        raise ValueError("DATABASE_URL is required to configure persistence")
    _database = build_database(url, echo=echo)
    return _database


def get_database() -> Database:
    """Return the configured database or raise if missing."""
    if _database is None:
        raise RuntimeError("database has not been configured")
    return _database


def reset_database() -> None:
    """Clear the process-wide database handle (tests only)."""
    global _database
    if _database is not None:
        _database.engine.dispose()
    _database = None


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped session."""
    database = get_database()
    session = database.create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
