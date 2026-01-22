
def test_security_headers(client):
    """Test that security headers are present in responses."""
    response = client.get("/health")
    assert response.status_code == 200

    headers = response.headers

    # Check for critical security headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
