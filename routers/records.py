"""
Records router — financial record CRUD and dashboard summary endpoints.

Access:
  GET  /records/              — viewer, analyst, admin (with filters)
  GET  /records/{id}          — viewer, analyst, admin
  POST /records/              — admin only
  PUT  /records/{id}          — admin only
  DELETE /records/{id}        — admin only
  GET  /records/summary       — viewer, analyst, admin
  GET  /records/by-category   — analyst, admin
  GET  /records/trends        — analyst, admin
  GET  /records/recent        — viewer, analyst, admin
"""

import logging
from collections import defaultdict
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Record, User
from routers.auth import is_auth, require_admin, require_analyst
from schema.records import RecordCreate, RecordOut, RecordType, RecordUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


# Helper


def _get_record_or_404(record_id: int, db: Session) -> Record:
    """Fetch a record by ID or raise a 404 error."""
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found."
        )
    return record


# CRUD


@router.get("/", response_model=List[RecordOut])
def list_records(
    type: Optional[RecordType] = Query(default=None, description="Filter by type: income | expense"),
    category: Optional[str] = Query(default=None, description="Partial category match"),
    from_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _: User = Depends(is_auth),) -> List[Record]:
    """
    List all financial records.
    Supports optional filters: type, category (partial), date range.
    All authenticated roles can access this endpoint.
    """
    query = db.query(Record)
    if type:
        query = query.filter(Record.type == type)
    if category:
        query = query.filter(Record.category.ilike(f"%{category}%"))
    if from_date:
        query = query.filter(Record.date >= from_date)
    if to_date:
        query = query.filter(Record.date <= to_date)
    return query.order_by(Record.date.desc()).all()


@router.get("/summary")
def summary(db: Session = Depends(get_db),_: User = Depends(is_auth),) -> dict:
    """
    Return total income, total expenses, net balance, and record count.
    All authenticated roles can access this endpoint.
    """
    records = db.query(Record).all()
    total_income = sum(r.amount for r in records if r.type == "income")
    total_expense = sum(r.amount for r in records if r.type == "expense")
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expense, 2),
        "net_balance": round(total_income - total_expense, 2),
        "record_count": len(records),
    }


@router.get("/by-category")
def by_category(
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst),
) -> dict:
    """
    Return total amounts grouped by category.
    Analyst and admin only.
    """
    records = db.query(Record).all()
    totals: dict[str, float] = defaultdict(float)
    for r in records:
        totals[r.category] = round(totals[r.category] + r.amount, 2)
    return {"by_category": dict(sorted(totals.items()))}


@router.get("/trends")
def trends(
    from_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst),
) -> dict:
    """
    Return monthly income vs expense totals bucketed by YYYY-MM.
    Analyst and admin only.
    """
    query = db.query(Record)
    if from_date:
        query = query.filter(Record.date >= from_date)
    if to_date:
        query = query.filter(Record.date <= to_date)

    monthly: dict[str, dict[str, float]] = defaultdict(
        lambda: {"income": 0.0, "expense": 0.0}
    )
    for r in query.all():
        bucket = r.date.strftime("%Y-%m")
        monthly[bucket][r.type] = round(monthly[bucket][r.type] + r.amount, 2)
    return {"trends": dict(sorted(monthly.items()))}


@router.get("/recent")
def recent(
    limit: int = Query(default=10, ge=1, le=50, description="Number of records to return"),
    db: Session = Depends(get_db),
    _: User = Depends(is_auth),
) -> dict:
    """
    Return the most recent financial records.
    All authenticated roles can access this endpoint.
    """
    records = (
        db.query(Record)
        .order_by(Record.date.desc(), Record.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "recent": [
            {
                "id": r.id,
                "amount": r.amount,
                "type": r.type,
                "category": r.category,
                "date": r.date.isoformat(),
                "notes": r.notes,
            }
            for r in records
        ]
    }


@router.get("/{record_id}", response_model=RecordOut)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(is_auth),
) -> Record:
    """
    Get a single financial record by ID.
    All authenticated roles can access this endpoint.
    """
    return _get_record_or_404(record_id, db)


@router.post("/", response_model=RecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Record:
    """
    Create a new financial record.
    Admin only.
    """
    record = Record(**payload.model_dump(), owner_id=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(
        "Record created: id=%s type=%s amount=%s", record.id, record.type, record.amount
    )
    return record


@router.put("/{record_id}", response_model=RecordOut)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Record:
    """
    Update an existing financial record.
    Admin only.
    """
    record = _get_record_or_404(record_id, db)

    update_data = payload.model_dump(exclude_unset=True)
    if "amount" in update_data and update_data["amount"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Amount must be greater than zero.",
        )
    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    logger.info("Record updated: id=%s", record_id)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    """
    Delete a financial record.
    Admin only.
    """
    record = _get_record_or_404(record_id, db)
    db.delete(record)
    db.commit()
    logger.info("Record deleted: id=%s", record_id)
