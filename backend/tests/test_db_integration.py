import pytest
from main import app

# DB setup and client are now in conftest.py


def test_student_lifecycle(client):
    """Test full lifecycle of a student: Login (create), Check Material (empty), Login again (retrieve)."""
    
    # 1. Login (Create) -> Now /register
    # Note: /register returns {access_token, user: {...}}
    response = client.post("/register", json={"name": "TestUser", "password": "StrongPass1!"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["name"] == "TestUser"
    assert "id" in data["user"]
    student_id = data["user"]["id"]
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Check Material (Should be empty initially)
    # The endpoint now expects token, not student_id param
    response = client.get("/current-material", headers=headers)
    assert response.status_code == 200
    assert response.json()["has_material"] is False
    
    # 3. Login again (Retrieve same user)
    response = client.post("/login", json={"name": "TestUser", "password": "StrongPass1!"})
    assert response.status_code == 200
    assert response.json()["user"]["id"] == student_id
