from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_cors_allowed_origin():
    """Test that a request from a valid origin is allowed."""
    headers = {"Origin": "http://localhost:5173"}
    # Use GET for simple CORS request
    response = client.get("/health", headers=headers)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert response.headers["access-control-allow-credentials"] == "true"

def test_cors_disallowed_origin():
    """Test that a request from an invalid origin is NOT allowed."""
    headers = {"Origin": "http://evil.com"}
    response = client.get("/health", headers=headers)

    # In strict mode, disallowed origins do not get ACAO header.
    # Currently this fails because it returns '*'
    assert "access-control-allow-origin" not in response.headers
