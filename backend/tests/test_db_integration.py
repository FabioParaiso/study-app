import pytest
from main import app

# DB setup and client are now in conftest.py


def test_student_lifecycle(client):
    """Test full lifecycle of a student: Login (create), Check Material (empty), Login again (retrieve)."""
    
    # 1. Login (Create) -> Now /register
    # Note: /register returns {access_token, user: {...}}
    import time
    name = f"TestUser{int(time.time()*1000)}"
    response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["name"] == name
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
    response = client.post("/login", json={"name": name, "password": "StrongPass1!"})
    assert response.status_code == 200
    assert response.json()["user"]["id"] == student_id


def test_activate_material_not_found_keeps_active(client):
    """Integration test: activate invalid material should keep active material and return 404."""
    import time
    name = f"ActiveMat{int(time.time()*1000)}"
    register_response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("test.txt", b"Content", "text/plain")}
    from main import app
    from modules.materials.deps import get_ai_service as materials_get_ai_service
    from unittest.mock import Mock

    mock_service = Mock()
    mock_service.is_available.return_value = True
    mock_service.extract_topics.return_value = {"Topic": ["Topic"]}
    app.dependency_overrides[materials_get_ai_service] = lambda: mock_service
    try:
        client.post("/upload", files=files, headers=headers)
    finally:
        app.dependency_overrides.pop(materials_get_ai_service, None)

    current = client.get("/current-material", headers=headers).json()
    assert current["has_material"] is True

    response = client.post("/materials/9999/activate", headers=headers)
    assert response.status_code == 404
    assert "Active material unchanged" in response.json()["detail"]

    current_after = client.get("/current-material", headers=headers).json()
    assert current_after["id"] == current["id"]
