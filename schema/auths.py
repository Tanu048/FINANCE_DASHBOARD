"""Pydantic schemas for authentication responses."""

from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response returned after a successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[str] = None
