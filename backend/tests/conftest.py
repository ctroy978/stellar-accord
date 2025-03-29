# File: tests/conftest.py
import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import app modules
from app.db.base import Base
from app.main import app
from app.db.session import get_db

# Use the same database URL as your app
TEST_DATABASE_URL = "postgresql://postgres:postgres@db:5432/stellar_accord"

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test function."""
    engine = create_engine(TEST_DATABASE_URL)
    
    # Create all tables for this test
    Base.metadata.create_all(engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.rollback()  # Roll back any uncommitted changes
        db.close()
        
        # Drop all tables after test to start fresh
        Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a FastAPI test client with a database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    
    # Reset the dependency override
    app.dependency_overrides = {}