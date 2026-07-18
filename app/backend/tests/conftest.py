import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.backend.models.base import Base
from app.backend.core.database import get_db
from app.backend.main import app

# Use an in-memory SQLite database for testing to ensure isolation and speed
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture that creates database tables before each test and drops them after.
    Yields a session maker for testing database.
    """
    print("DEBUG - Metadata tables before create_all:", list(Base.metadata.tables.keys()))
    Base.metadata.create_all(bind=engine)
    print("DEBUG - Metadata tables after create_all:", list(Base.metadata.tables.keys()))
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture that returns a TestClient with overridden get_db dependency.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
