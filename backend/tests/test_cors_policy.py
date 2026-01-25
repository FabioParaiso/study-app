import pytest
import os
from unittest.mock import patch

def test_cors_allowed_origin(client):
    """
    Test that a request from an allowed origin receives the correct CORS headers.
    """
    # The default behavior in our new implementation should be allowing localhost:5173
    # Note: If ALLOWED_ORIGINS is not set in env, it defaults to localhost:5173

    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    }

    # We use OPTIONS (preflight) or just a simple GET to check headers
    response = client.options("/health", headers=headers)

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"

def test_cors_disallowed_origin(client):
    """
    Test that a request from a disallowed origin does NOT receive the allow-origin header
    for that origin.
    """
    headers = {
        "Origin": "http://evil.com",
        "Access-Control-Request-Method": "GET",
    }

    response = client.options("/health", headers=headers)

    # In strict CORS, it shouldn't return the ACAO header for evil.com
    # It might return nothing, or just not match.
    allow_origin = response.headers.get("access-control-allow-origin")
    assert allow_origin != "http://evil.com"
