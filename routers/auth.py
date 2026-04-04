"""
Auth router — register, login, and current-user endpoints.

Access:
  POST /auth/register — public
  POST /auth/login    — public
  GET  /auth/me       — any authenticated user
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import User
from schema.auths import Token
from schema.users import UserCreate, UserLogin, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_hasher = PasswordHasher()

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY")
ALGORITHM: str = os.getenv("ALGORITHM")
EXPIRE_MINUTES: int = int(os.getenv("EXPIRE_MINUTES", "60"))
ADMIN_KEY: str = os.getenv("ADMIN_KEY")

# Helpers

def hash_password(plain: str) -> str:
    """Hash a plain-text password using Argon2id."""
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Return True if the plain password matches the Argon2 hash.
    Returns False for any mismatch — never raises to the caller.
    """
    try:
        return _hasher.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_access_token(username: str, role: str) -> tuple[str, str]:
    """
    Create a signed JWT for the given user.
    Returns (token_string, expiry_iso_string).
    """
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    payload = {"sub": username, "role": role, "exp": expires_at}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expires_at.isoformat()


def is_auth(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — resolve a Bearer token to a User row.
    Raises 401 if the token is missing, invalid, or expired.
    Raises 403 if the account is inactive.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )

    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive."
        )
    return user


def require_analyst(current_user: User = Depends(is_auth)) -> User:
    """
    FastAPI dependency — allow analyst and admin only.
    Raises 403 for viewers.
    """
    if current_user.role == "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst or admin access required.",
        )
    return current_user


def require_admin(current_user: User = Depends(is_auth)) -> User:
    """
    FastAPI dependency — allow admin only.
    Raises 403 for viewer and analyst.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required."
        )
    return current_user


# Routes

@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Register a new user account.

    - Viewer: no key required.
    - Analyst: requires ANALYST_KEY in admin_key field.
    - Admin: requires ADMIN_KEY in admin_key field.
    - Username and email must be unique.
    - Password is hashed with Argon2 before storage.
    """
    if user_in.role == "admin" or user_in.role == "analyst":
        if not user_in.admin_key or user_in.admin_key != ADMIN_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key."
            )

    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered."
        )
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken."
        )

    user = User(
        name=user_in.name,
        username=user_in.username,
        email=user_in.email,
        password=hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("New user registered: %s (role=%s)", user.username, user.role)
    return user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(data: UserLogin, db: Session = Depends(get_db)) -> dict:
    """
    Authenticate with username and password.
    Returns a signed JWT token on success.
    """
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        logger.warning("Failed login attempt for username: %s", data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive."
        )

    token, expires_at = create_access_token(user.username, user.role)
    logger.info("User logged in: %s", user.username)
    return {"access_token": token, "token_type": "bearer", "expires_in": expires_at}


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def me(current_user: User = Depends(is_auth)) -> User:
    """Return the currently authenticated user's profile."""
    return current_user
