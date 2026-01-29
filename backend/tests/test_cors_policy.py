from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_cors_allowed_origin():
    # Test with a default allowed origin
    origin = "http://localhost:5173"
    response = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin

def test_cors_disallowed_origin():
    # Test with a disallowed origin
    origin = "http://evil.com"
    response = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    # FastAPI/Starlette usually returns 200 or 400 but WITHOUT the allow-origin header for disallowed origins
    # or it might return 400 if configured strictly.
    # The key is that Access-Control-Allow-Origin should NOT be present or should not match the request origin.

    # Starlette CORSMiddleware returns 400 for disallowed origins on preflight
    if response.status_code == 200:
        assert "access-control-allow-origin" not in response.headers
    else:
        assert response.status_code == 400
