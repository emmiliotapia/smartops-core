"""
pytest configuration and fixtures.
"""

import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

# Add app directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# IMPORTANT: Import AFTER path is set
from app.database import Base, engine as prod_engine, SessionLocal as ProdSessionLocal, get_db
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def test_config():
    """Load test configuration."""
    os.environ["OPENAI_API_KEY"] = "test-key-for-unit-tests"
    return {
        "database_url": "sqlite:///:memory:",
        "debug": True,
    }


@pytest.fixture(scope="function")
def test_db_engine():
    """Create test database engine with all tables."""
    # Create in-memory SQLite engine
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create ALL tables
    Base.metadata.create_all(bind=test_engine)
    
    TestSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    
    # Override get_db globally for this test
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Apply override to app
    app.dependency_overrides[get_db] = override_get_db
    
    # Yield engine for test to use
    yield test_engine
    
    # Cleanup
    app.dependency_overrides.clear()
    test_engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_db_engine):
    """Get a session from test database."""
    TestSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_db_engine
    )
    db = TestSessionLocal()
    yield db
    db.close()
