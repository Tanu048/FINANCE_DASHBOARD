import os

# FORCE ENV VARIABLES FOR TESTS
os.environ["ADMIN_KEY"] = "admin-secret"
os.environ["ANALYST_KEY"] = "analyst-secret"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ALGORITHM"] = "HS256"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database.db import get_db
from database.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(bind=engine)


# RESET DB BEFORE EACH TEST
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def create_user(client):
    def _create_user(role="viewer", username="user", email=None):
        if email is None:
            email = f"{username}@test.com"

        payload = {
            "name": "Test User",
            "username": username,
            "email": email,
            "password": "password123",
            "role": role,
        }

        if role == "admin":
            payload["admin_key"] = "admin-secret"
        elif role == "analyst":
            payload["admin_key"] = "analyst-secret"

        res = client.post("/auth/register", json=payload)

        # FAIL FAST if user not created
        assert res.status_code == 201, res.text

        return res.json()

    return _create_user


@pytest.fixture
def get_token(client):
    def _login(username, password="password123"):
        res = client.post("/auth/login", json={
            "username": username,
            "password": password
        })

        assert res.status_code == 200, res.text

        return res.json()["access_token"]

    return _login