"""
Pytest configuration and shared fixtures.
Uses in-memory SQLite with StaticPool so all connections share one DB.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
from fastapi.testclient import TestClient

# StaticPool = single connection reused across all requests.
# This is required for in-memory SQLite so setup_db and get_db see the same DB.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch DB module BEFORE importing FastAPI app so the lifespan uses test_engine.
import app.database as db_module

db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal

from app.database import get_db
from app.main import app


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test and drop them after."""
    db_module.Base.metadata.create_all(bind=test_engine)
    yield
    db_module.Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(setup_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
    client.post("/register", json=payload)
    return payload


@pytest.fixture
def auth_headers(client, registered_user):
    res = client.post(
        "/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
