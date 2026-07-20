"""
backend/tests/test_memory.py

Unit tests for database-backed user memory (UserMemory).
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.database import Base
from backend.models.user import User
from backend.models.user_memory import UserMemory
from backend.ai.memory import DatabaseMemory

# Use in-memory SQLite for testing DB memory
DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="db_session")
def fixture_db_session():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    
    # Create test user
    test_user = User(email="test@example.com", hashed_password="fakehashedpassword", name="Test User")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_get_or_create_profile(db_session):
    """get_or_create_profile initializes a new UserMemory profile if none exists."""
    db_memory = DatabaseMemory(db_session)
    user = db_session.query(User).first()
    
    # Verify no profile exists initially
    existing = db_session.query(UserMemory).filter(UserMemory.user_id == user.id).first()
    assert existing is None
    
    # Retrieve or create profile
    profile = await db_memory.get_or_create_profile(user.id)
    assert profile is not None
    assert profile["preferences"] == {}
    assert profile["streak_days"] == 0
    
    # Verify it now exists in DB
    created = db_session.query(UserMemory).filter(UserMemory.user_id == user.id).first()
    assert created is not None
    assert created.user_id == user.id

@pytest.mark.asyncio
async def test_update_preferences(db_session):
    """update_preferences correctly updates and persists preferences."""
    db_memory = DatabaseMemory(db_session)
    user = db_session.query(User).first()
    
    # Initialize profile
    await db_memory.get_or_create_profile(user.id)
    
    # Update preferences
    new_pref = {"study_speed": "fast", "daily_study_hours": 3.0}
    await db_memory.update_preferences(user.id, new_pref)
    
    # Verify updates
    profile = await db_memory.get_user_profile(user.id)
    assert profile["preferences"]["study_speed"] == "fast"
    assert profile["preferences"]["daily_study_hours"] == 3.0

@pytest.mark.asyncio
async def test_increment_streak(db_session):
    """increment_streak increments streak metrics correctly."""
    db_memory = DatabaseMemory(db_session)
    user = db_session.query(User).first()
    
    # Initialize profile
    await db_memory.get_or_create_profile(user.id)
    
    # Increment once
    streak1 = await db_memory.increment_streak(user.id)
    assert streak1 == 1
    
    # Increment twice
    streak2 = await db_memory.increment_streak(user.id)
    assert streak2 == 2
    
    # Verify persisted values
    record = db_session.query(UserMemory).filter(UserMemory.user_id == user.id).first()
    assert record.streak_days == 2
    assert record.longest_streak == 2
