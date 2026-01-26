from fastapi.testclient import TestClient
from main import app

def test_cors_allowed_origin(client):
    """Test that a request from an allowed origin is accepted and has correct headers."""
    # Based on planned default allowed origins
    origin = "http://localhost:5173"
    response = client.get("/health", headers={"Origin": origin})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"

def test_cors_disallowed_origin(client):
    """Test that a request from a disallowed origin is not granted CORS headers."""
    origin = "http://evil.com"
    response = client.get("/health", headers={"Origin": origin})
    assert response.status_code == 200
    # The middleware should NOT set Access-Control-Allow-Origin for disallowed domains
    assert "access-control-allow-origin" not in response.headers
