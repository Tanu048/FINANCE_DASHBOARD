"""
Users router — admin-only user management endpoints.

Access:
  GET    /users/list     — admin only
  PUT    /users/{id}     — admin only
  DELETE /users/{id}     — admin only
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User
from routers.auth import require_admin
from schema.users import UserResponse, UserUpdate

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/list", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> List[User]:
    """
    Return all registered users.
    Admin only.
    """
    return db.query(User).order_by(User.created_at.desc()).all()


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    """
    Update a user's role or active status.
    Admin only.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    logger.info("User updated: id=%s changes=%s", user_id, update_data)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """
    Delete a user and all their records (cascade).
    Admin only. Cannot delete your own account.
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    db.delete(user)
    db.commit()
    logger.info("User deleted: id=%s by admin=%s", user_id, current_user.username)
