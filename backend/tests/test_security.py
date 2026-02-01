import pytest
from unittest.mock import patch, Mock
from services.usage_service import UsageLimitReached
from modules.materials.deps import get_ai_service as materials_get_ai_service

# client comes from conftest

def _override_material_ai(client, topics=None):
    mock_service = Mock()
    mock_service.is_available.return_value = True
    mock_service.extract_topics.return_value = topics or {"Test": ["Test"]}
    client.app.dependency_overrides[materials_get_ai_service] = lambda: mock_service
    return mock_service

def _clear_material_ai_override(client):
    client.app.dependency_overrides.pop(materials_get_ai_service, None)


def test_upload_small_file(client, auth_headers):
    """Test that a small file upload works as expected."""
    content = b"Hello world"
    files = {"file": ("test.txt", content, "text/plain")}
    # Remove student_id from data, rely on token
    _override_material_ai(client)
    try:
        response = client.post("/upload", files=files, headers=auth_headers)
    finally:
        _clear_material_ai_override(client)
    assert response.status_code == 200
    assert response.json()["text"] == "Hello world"

def test_upload_too_large_file(client, auth_headers):
    """Test that uploading a file exceeding the limit returns 413."""
    # Create a dummy content slightly larger than 10MB
    # 10MB = 10 * 1024 * 1024 = 10485760 bytes
    # We'll use 10.1MB
    large_content = b"x" * (10 * 1024 * 1024 + 100)
    files = {"file": ("large.txt", large_content, "text/plain")}

    _override_material_ai(client)
    try:
        response = client.post("/upload", files=files, headers=auth_headers)
    finally:
        _clear_material_ai_override(client)

    # Currently this will likely pass (200) or fail with 500 if memory is issue,
    # but we want 413.
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

@patch("modules.materials.document_service.PdfReader")
def test_upload_exception_handling(mock_pdf_reader, client, auth_headers):
    """Test that exceptions are masked and return 500 without leaking details."""
    # Simulate a sensitive error
    mock_pdf_reader.side_effect = Exception("Database connection failed at 192.168.1.5")

    # Upload a PDF to trigger the mocked PDF processing
    files = {"file": ("test.pdf", b"%PDF-1.4...", "application/pdf")}

    _override_material_ai(client)
    try:
        response = client.post("/upload", files=files, headers=auth_headers)
    finally:
        _clear_material_ai_override(client)

    # DocumentService catches the exception and returns None
    # Main.py sees None and raises 400 "Failed to extract text from file."
    # This is secure as it doesn't leak the exception.
    assert response.status_code == 400
    # Ensure sensitive info is NOT leaked
    assert "192.168.1.5" not in response.text
    assert "Failed to extract text" in response.json()["detail"]


@patch("modules.materials.document_service.PdfReader")
def test_upload_pdf_with_no_text_returns_400(mock_pdf_reader, client, auth_headers):
    page = Mock()
    page.extract_text.return_value = None
    reader_instance = Mock()
    reader_instance.pages = [page]
    mock_pdf_reader.return_value = reader_instance

    files = {"file": ("empty.pdf", b"%PDF-1.4...", "application/pdf")}
    _override_material_ai(client)
    try:
        response = client.post("/upload", files=files, headers=auth_headers)
    finally:
        _clear_material_ai_override(client)

    assert response.status_code == 400
    assert "Failed to extract text" in response.json()["detail"]


def test_upload_unknown_file_type_defaults_to_text(client, auth_headers):
    content = b"Hello unknown type"
    files = {"file": ("file.unknown", content, "application/octet-stream")}
    _override_material_ai(client)
    try:
        response = client.post("/upload", files=files, headers=auth_headers)
    finally:
        _clear_material_ai_override(client)

    assert response.status_code == 200
    assert response.json()["text"] == "Hello unknown type"


def test_upload_invalid_text_returns_400(client, auth_headers):
    invalid_bytes = b"\xff\xfe\xfa\xfb"
    files = {"file": ("bad.txt", invalid_bytes, "text/plain")}
    _override_material_ai(client)
    try:
        response = client.post("/upload", files=files, headers=auth_headers)
    finally:
        _clear_material_ai_override(client)

    assert response.status_code == 400
    assert "Failed to extract text" in response.json()["detail"]


def test_protected_endpoint_requires_auth(client):
    response = client.get("/current-material")
    assert response.status_code == 401


def test_invalid_token_rejected(client):
    response = client.get("/current-material", headers={"Authorization": "Bearer badtoken"})
    assert response.status_code == 401


def test_ai_quota_exceeded_returns_429(client, auth_headers):
    # Override UsageService to simulate limit reached
    class FakeUsageService:
        def check_and_increment(self, student_id: int):
            raise UsageLimitReached(limit=1)

    # Override usage service where it is used in dependencies
    from dependencies import get_usage_service as deps_get_usage_service
    client.app.dependency_overrides[deps_get_usage_service] = lambda: FakeUsageService()
    try:
        content = b"Hello world"
        files = {"file": ("test.txt", content, "text/plain")}
        # Override via dependency injection to avoid direct module patching
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.extract_topics.return_value = {"Test": ["Test"]}
        client.app.dependency_overrides[materials_get_ai_service] = lambda: mock_service
        try:
            response = client.post("/upload", files=files, headers=auth_headers)
        finally:
            client.app.dependency_overrides.pop(materials_get_ai_service, None)
        assert response.status_code == 429
        assert "Limite diario" in response.json()["detail"]
    finally:
        client.app.dependency_overrides.pop(deps_get_usage_service, None)


def test_quiz_generation_quota_exceeded_returns_429(client, auth_headers):
    class FakeUsageService:
        def check_and_increment(self, student_id: int):
            raise UsageLimitReached(limit=1)

    from dependencies import get_usage_service as deps_get_usage_service
    client.app.dependency_overrides[deps_get_usage_service] = lambda: FakeUsageService()
    try:
        # Upload material first
        files = {"file": ("test.txt", b"Content", "text/plain")}
        from modules.materials.deps import get_ai_service as materials_get_ai_service
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.extract_topics.return_value = {"Topic": ["Topic"]}
        client.app.dependency_overrides[materials_get_ai_service] = lambda: mock_service
        try:
            client.post("/upload", files=files, headers=auth_headers)
        finally:
            client.app.dependency_overrides.pop(materials_get_ai_service, None)

        # Attempt generate quiz should fail with 429
        quiz_request = {
            "topics": [],
            "quiz_type": "multiple-choice",
            "api_key": "sk-test"
        }
        response = client.post("/generate-quiz", json=quiz_request, headers=auth_headers)
        assert response.status_code == 429
        assert "Limite diario" in response.json()["detail"]
    finally:
        client.app.dependency_overrides.pop(deps_get_usage_service, None)
