"""SQLAlchemy engine and session management."""

from collections.abc import Generator
from functools import lru_cache
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from masar.config.settings import get_settings


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy database models."""

    pass


def normalize_database_url(url: str) -> str:
    """Ensure standard postgresql:// URLs use psycopg2 driver."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


@lru_cache()
def get_engine(database_url: str) -> Engine:
    """Create and cache a SQLAlchemy engine for a database URL."""
    url = normalize_database_url(database_url)
    connect_args: dict[str, Any] = {}
    engine_kwargs: dict[str, Any] = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if url in ("sqlite://", "sqlite:///:memory:"):
            engine_kwargs["poolclass"] = StaticPool
    return create_engine(url, connect_args=connect_args, **engine_kwargs)


def get_session_factory(database_url: str) -> sessionmaker[Session]:
    """Return a sessionmaker bound to the given database URL."""
    engine = get_engine(database_url)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db(database_url: str | None = None) -> Generator[Session, None, None]:
    """Dependency helper yielding an active database session."""
    url = database_url or get_settings().database_url
    factory = get_session_factory(url)
    session = factory()
    try:
        yield session
    finally:
        session.close()
