import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
from pathlib import Path
# Ensure we can import from local modules
sys.path.append(str(Path(__file__).parent))

from database import Base, get_db
from main import app
import models

# Setup in-memory DB
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

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_student_lifecycle():
    """Test full lifecycle of a student: Login (create), Check Material (empty), Login again (retrieve)."""
    
    # 1. Login (Create)
    response = client.post("/students", json={"name": "TestUser"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestUser"
    assert "id" in data
    student_id = data["id"]
    
    # 2. Check Material (Should be empty initially)
    # The endpoint expects student_id as query param based on main.py: 
    # def get_current_material(student_id: int, ...)
    response = client.get(f"/current-material?student_id={student_id}")
    assert response.status_code == 200
    assert response.json()["has_material"] is False
    
    # 3. Login again (Retrieve same user)
    response = client.post("/students", json={"name": "TestUser"})
    assert response.status_code == 200
    assert response.json()["id"] == student_id
