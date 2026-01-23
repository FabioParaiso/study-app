from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_security_headers():
    response = client.get("/health")
    assert response.status_code == 200

    # Check for missing security headers
    headers = response.headers
    assert "X-Content-Type-Options" in headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in headers
    assert headers["X-Frame-Options"] == "DENY"
    assert "X-XSS-Protection" in headers
    assert headers["X-XSS-Protection"] == "1; mode=block"
    assert "Referrer-Policy" in headers
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
