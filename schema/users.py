"""Pydantic schemas for user-related requests and responses."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserRole(str, Enum):
    """Allowed roles in the system."""

    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"


class UserCreate(BaseModel):
    """Schema for registering a new user."""

    name: str
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.viewer
    admin_key: Optional[str] = None  # required when role is admin or analyst

    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v: str) -> str:
        """Reject usernames that contain spaces."""
        if " " in v:
            raise ValueError("Username must not contain spaces.")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        """Require passwords to be at least 6 characters."""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters.")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user's role or active status. Admin only."""

    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema returned in user-related responses."""

    id: int
    name: str
    username: str
    email: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """Schema for login requests."""

    username: str
    password: str
