import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os
from pathlib import Path

# Set TEST_MODE to disable rate limiting
os.environ["TEST_MODE"] = "true"

# Fix path to import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from database import Base, get_db
from main import app
import models # Register tables for Base.metadata.create_all
from modules.materials.deps import get_ai_service

# Setup in-memory DB for ALL tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Mock AI Service
class MockTopicAIService:
    def is_available(self) -> bool:
        return True
    def extract_topics(self, text: str) -> dict:
        return {"General": ["Mock Concept"]}

def override_get_ai_service():
    return MockTopicAIService()

# Apply valid overrides globally for testing (this might be overwritten if main is reloaded)
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_ai_service] = override_get_ai_service

@pytest.fixture
def db_session():
    """Fixture to provide database session per test."""
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="session")
def client():
    # Strategy: Mock slowapi.Limiter so decorators don't register limits
    import slowapi
    from unittest.mock import MagicMock
    
    # Save original
    original_limiter = slowapi.Limiter
    
    # Replace with a dummy that returns a no-op decorator
    class DummyLimiter:
        def __init__(self, key_func=None, **kwargs):
            self.enabled = False
            
        def limit(self, limit_value, **kwargs):
            # Return a decorator that does nothing
            def decorator(func):
                return func
            return decorator
            
    slowapi.Limiter = DummyLimiter
    
    # Reload modules to apply the mock
    import sys
    import main
    from importlib import reload
    import modules.auth.router
    
    # Force reload main and routers where limiter is used
    reload(modules.auth.router)
    reload(main)
    
    # Re-apply overrides to the reloaded app instance
    from modules.materials.deps import get_ai_service
    from database import get_db

    main.app.dependency_overrides[get_ai_service] = override_get_ai_service
    main.app.dependency_overrides[get_db] = override_get_db

    yield TestClient(main.app)
    
    # Restore original (optional, but good practice)
    slowapi.Limiter = original_limiter

@pytest.fixture(autouse=True)
def init_db():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers(client):
    """Helper to get auth headers for tests."""
    client.post("/register", json={"name": "AuthTest", "password": "StrongPass1!"})
    response = client.post("/login", json={"name": "AuthTest", "password": "StrongPass1!"})
    token = response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}
