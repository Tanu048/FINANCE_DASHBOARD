"""
SQLAlchemy ORM models.

Tables:
  users   — accounts with role-based access (viewer | analyst | admin)
  records — financial entries (income or expense)
"""

from datetime import date as Date, datetime, timezone

from sqlalchemy import Boolean,Column,Date,DateTime,Float,ForeignKey,Integer,String
from sqlalchemy.orm import declarative_base, relationship

Base=declarative_base()

class User(Base):
    """Represents a user account in the system."""

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)
    username: str = Column(String, unique=True, index=True, nullable=False)
    email: str = Column(String, unique=True, index=True, nullable=False)
    password: str = Column(String, nullable=False)
    role: str = Column(String, default="viewer")  # viewer | analyst | admin
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    records = relationship(
        "Record", back_populates="owner", cascade="all, delete-orphan"
    )


class Record(Base):
    """Represents a single financial entry (income or expense)."""

    __tablename__ = "records"

    id: int = Column(Integer, primary_key=True, index=True)
    amount: float = Column(Float, nullable=False)
    type: str = Column(String, nullable=False)  # income | expense
    category: str = Column(String, nullable=False)
    date: Date = Column(Date, nullable=False)
    notes: str = Column(String, default="")
    owner_id: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="records")
