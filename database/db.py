"""
Database configuration.

Uses SQLite via SQLAlchemy — no external service required.
To switch to PostgreSQL, set DATABASE_URL in your .env file and
remove the connect_args parameter from create_engine().
"""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finance.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(engine)

def create_tables() -> None:
    """Create all tables defined in models. Called once on startup."""
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created (or already exist).")


def get_db():
    """
    FastAPI dependency — yields a database session per request.
    Closes the session automatically after the request completes.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
