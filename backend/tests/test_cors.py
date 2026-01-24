from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_cors_allowed_origin():
    """Test that a request from an allowed origin receives the correct CORS headers."""
    origin = "http://localhost:5173"
    response = client.get("/health", headers={"Origin": origin})

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == origin

def test_cors_disallowed_origin():
    """Test that a request from a disallowed origin does NOT receive CORS headers."""
    origin = "http://evil-site.com"
    response = client.get("/health", headers={"Origin": origin})

    assert response.status_code == 200
    # The middleware should NOT add the CORS headers for disallowed origins
    assert "access-control-allow-origin" not in response.headers
