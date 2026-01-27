from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_cors_allowed_origin():
    """Test that a trusted origin is allowed."""
    # We need to simulate the environment or ensure the default includes this
    # But since we are modifying the code to USE env vars, let's just test against
    # what we EXPECT the default to be (localhost:5173).

    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/health", headers=headers)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

def test_cors_disallowed_origin():
    """Test that an untrusted origin is NOT allowed."""
    headers = {
        "Origin": "http://evil.com",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/health", headers=headers)

    # In a strict CORS setup, the server should either not return the header
    # or return a specific allowed origin (not evil.com).
    allow_origin = response.headers.get("access-control-allow-origin")

    # It should NOT be evil.com
    assert allow_origin != "http://evil.com"
    # It should NOT be *
    assert allow_origin != "*"
