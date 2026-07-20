"""
backend/core/database.py

SQLAlchemy engine, session factory, and base model for Syllabot.

Supports both:
  - SQLite  (local development): sqlite:///./syllabot.db
  - PostgreSQL (production):     postgresql+psycopg2://user:pass@host:5432/dbname

The DATABASE_URL environment variable controls which database is used.
See .env.example for configuration details.
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.core.config import settings

# ── Engine configuration ──────────────────────────────────────────────────────

def _build_engine_kwargs() -> dict:
    """
    Build SQLAlchemy engine kwargs appropriate for the configured database.

    SQLite requires check_same_thread=False for multi-threaded FastAPI use.
    PostgreSQL benefits from connection pooling for production workloads.
    """
    url = settings.DATABASE_URL

    if url.startswith("sqlite"):
        # SQLite: minimal config, thread-safety override required
        return {
            "connect_args": {"check_same_thread": False}
        }

    # PostgreSQL / other relational databases
    return {
        "pool_size": 5,           # Maintain up to 5 persistent connections
        "max_overflow": 10,       # Allow up to 10 extra connections under load
        "pool_pre_ping": True,    # Verify connections before use (handles stale connections)
        "pool_recycle": 1800,     # Recycle connections after 30 minutes
    }


engine = create_engine(
    settings.DATABASE_URL,
    **_build_engine_kwargs()
)

# ── Session factory ───────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ── Declarative base ──────────────────────────────────────────────────────────

Base = declarative_base()


# ── FastAPI dependency ────────────────────────────────────────────────────────

def get_db():
    """
    FastAPI dependency that provides a database session per request.
    Automatically closes the session when the request is complete.

    Usage in route handlers:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
