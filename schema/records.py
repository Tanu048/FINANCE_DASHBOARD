"""Pydantic schemas for financial record requests and responses."""

from datetime import date as Date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class RecordType(str, Enum):
    """Allowed financial record types."""

    income = "income"
    expense = "expense"


class RecordCreate(BaseModel):
    """Schema for creating a new financial record. Admin only."""

    amount: float
    type: RecordType
    category: str
    date: Date
    notes: Optional[str] = ""

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        """Reject zero or negative amounts."""
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def category_not_blank(cls, v: str) -> str:
        """Reject blank or whitespace-only category strings."""
        if not v.strip():
            raise ValueError("Category must not be empty.")
        return v.strip().lower()


class RecordUpdate(BaseModel):
    """Schema for partially updating a financial record. Admin only."""

    amount: Optional[float] = None
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date: Optional[Date] = None
    notes: Optional[str] = None


class RecordOut(BaseModel):
    """Schema returned in record-related responses."""

    id: int
    amount: float
    type: RecordType
    category: str
    date: Date
    notes: str
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
