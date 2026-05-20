"""
SQLite database setup for local runtime storage.

Safety note:
- This module does not execute shell commands.
- It does not read arbitrary user files.
- It only manages the configured local SQLite database.
"""

import os
from collections.abc import Generator

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import models  # noqa: F401

DB_PATH = os.getenv("DB_PATH", "sqlite:///./dragon_pet_ai.db")


def create_db_engine(db_path: str = DB_PATH):
    """
    Create a SQLite engine.

    In-memory SQLite uses StaticPool so tests keep the same database across
    sessions and TestClient requests.
    """
    kwargs = {
        "echo": False,
        "connect_args": {"check_same_thread": False},
    }
    if db_path == "sqlite:///:memory:":
        kwargs["poolclass"] = StaticPool
    return create_engine(db_path, **kwargs)


engine = create_db_engine()


def init_db(db_engine=None) -> None:
    """Create local SQLite tables for conversation history, state, and memory."""
    SQLModel.metadata.create_all(db_engine or engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
