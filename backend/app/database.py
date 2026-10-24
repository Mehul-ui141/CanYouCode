"""Database configuration.

Uses SQLite for the MVP — no separate database server to install or manage.
The same engine config migrates to PostgreSQL later by changing only the
DATABASE_URL env var.

Note: check_same_thread=False is required because SQLite connections are not
thread-safe, and FastAPI's async workers spawn multiple threads.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# Sync engine. We run the analysis as sync CPU-bound work in a thread pool,
# so a sync engine is fine. Async engines exist but add complexity we don't need.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Per-thread session factory. Each request gets its own Session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


def get_db():
    """Dependency for FastAPI to get a fresh DB session per request.

    The session is automatically closed after the request completes, so each
    review gets a clean transactional context.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db():
    """Create all tables. Call once at startup (see main.py lifespan)."""
    Base.metadata.create_all(bind=engine)
