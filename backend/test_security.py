from fastapi.testclient import TestClient
from main import app, MAX_FILE_SIZE
from unittest.mock import patch, MagicMock
import pytest

client = TestClient(app)

def test_upload_exception_handling():
    # Verify that the application now hides exception details
    with patch('main.save_study_material', side_effect=Exception("SecretDBPassword")):
        files = {'file': ('test.txt', b"content", "text/plain")}
        response = client.post("/upload", files=files)
        assert response.status_code == 500
        # Secure behavior: expecting the secret NOT to be in the response
        assert "SecretDBPassword" not in response.json()['detail']
        assert response.json()['detail'] == "Internal Server Error"

def test_upload_file_size_limit():
    # Verify file size limit
    # We create a content slightly larger than MAX_FILE_SIZE
    # Since passing huge data in test client is heavy, we can mock the behavior or reduce the limit for test.
    # But since MAX_FILE_SIZE is imported in main.py, we can patch it?
    # Modifying global variables in imported modules is tricky in tests.

    # Let's try to mock the file read or content length check.
    # We implemented `if len(content) > MAX_FILE_SIZE:`

    # We can mock `file.read` to return a large bytes object (mock object that has length but not memory?)
    # No, len() calls __len__.

    # Let's use a mock file that returns a large content when read,
    # but we can't easily mock `file.read` inside `upload_file` without patching `UploadFile`?
    # `file` is an argument.

    # Alternatively, we can patch MAX_FILE_SIZE in `main`.
    with patch('main.MAX_FILE_SIZE', 10): # Set limit to 10 bytes
         files = {'file': ('test.txt', b"This is longer than 10 bytes", "text/plain")}
         response = client.post("/upload", files=files)
         assert response.status_code == 413
         assert response.json()['detail'] == "File too large"
