"""
Database initialization placeholder.

TASK-003: SQLModel engine setup — SQLite only, no tables yet.
Tables and schema migrations will be added in TASK-005 (Phase 3).

Safety note:
- This module does NOT execute shell commands.
- It does NOT read arbitrary user files.
- It only manages a local SQLite file at the configured DB_PATH.
"""

import os
from sqlmodel import create_engine, SQLModel

# Database path — can be overridden via environment variable DB_PATH
DB_PATH = os.getenv("DB_PATH", "sqlite:///./dragon_pet_ai.db")

# connect_args is required for SQLite to support multi-threaded access in FastAPI
engine = create_engine(
    DB_PATH,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """
    Initialize the database.

    TASK-003: Creates the SQLite file and runs SQLModel metadata setup.
    No tables are defined yet — this is a placeholder for Phase 3.
    """
    # SQLModel.metadata.create_all(engine) will activate once models are added.
    # For now, just validate the engine can connect.
    SQLModel.metadata.create_all(engine)
