import pytest
from unittest.mock import patch
from main import app

# client comes from conftest


def test_upload_small_file(client, auth_headers):
    """Test that a small file upload works as expected."""
    content = b"Hello world"
    files = {"file": ("test.txt", content, "text/plain")}
    # Remove student_id from data, rely on token
    response = client.post("/upload", files=files, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["text"] == "Hello world"

def test_upload_too_large_file(client, auth_headers):
    """Test that uploading a file exceeding the limit returns 413."""
    # Create a dummy content slightly larger than 10MB
    # 10MB = 10 * 1024 * 1024 = 10485760 bytes
    # We'll use 10.1MB
    large_content = b"x" * (10 * 1024 * 1024 + 100)
    files = {"file": ("large.txt", large_content, "text/plain")}

    response = client.post("/upload", files=files, headers=auth_headers)

    # Currently this will likely pass (200) or fail with 500 if memory is issue,
    # but we want 413.
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

@patch("services.document_service.PdfReader")
def test_upload_exception_handling(mock_pdf_reader, client, auth_headers):
    """Test that exceptions are masked and return 500 without leaking details."""
    # Simulate a sensitive error
    mock_pdf_reader.side_effect = Exception("Database connection failed at 192.168.1.5")

    # Upload a PDF to trigger the mocked PDF processing
    files = {"file": ("test.pdf", b"%PDF-1.4...", "application/pdf")}

    response = client.post("/upload", files=files, headers=auth_headers)

    # DocumentService catches the exception and returns None
    # Main.py sees None and raises 400 "Failed to extract text from file."
    # This is secure as it doesn't leak the exception.
    assert response.status_code == 400
    # Ensure sensitive info is NOT leaked
    assert "192.168.1.5" not in response.text
    assert "Failed to extract text" in response.json()["detail"]
