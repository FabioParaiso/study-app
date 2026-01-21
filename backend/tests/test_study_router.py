import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from main import app
from services.document_service import DocumentService
from services.topic_service import TopicService
from services.ai_service import AIService
import asyncio

# Use TestClient for synchronous testing of the async endpoint (it handles the loop)
# But we want to ensure that if we patch with an async mock or check calls, it works.

client = TestClient(app)

@pytest.fixture
def mock_doc_service():
    with patch("routers.study.DocumentService") as mock:
        instance = mock.return_value
        instance.extract_text.return_value = "Extracted Text Content"
        yield instance

@pytest.fixture
def mock_topic_service():
    with patch("routers.study.TopicService") as mock:
        instance = mock.return_value
        instance.extract_topics.return_value = ["Topic 1", "Topic 2"]
        yield instance

@pytest.fixture
def mock_repo():
    with patch("routers.study.MaterialRepository") as mock:
        yield mock.return_value

@pytest.fixture
def mock_quiz_repo():
    with patch("routers.study.QuizRepository") as mock:
        yield mock.return_value

def test_upload_file_successful(mock_doc_service, mock_topic_service, mock_repo, mock_quiz_repo):
    # This test verifies the endpoint works logic-wise.
    # It doesn't prove non-blocking behavior by itself, but verifies the refactor doesn't break logic.

    file_content = b"fake pdf content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    data = {"student_id": "123"}

    # Mock services
    mock_doc_service.extract_text.return_value = "Extracted Text Content"
    mock_topic_service.extract_topics.return_value = ["Topic 1", "Topic 2"]

    response = client.post("/upload", files=files, data=data)

    assert response.status_code == 200
    assert response.json()["text"] == "Extracted Text Content"
    assert response.json()["topics"] == ["Topic 1", "Topic 2"]

    # Check that services were called
    # Note: When using asyncio.to_thread, the mock is still called.
    mock_doc_service.extract_text.assert_called_once()
    mock_topic_service.extract_topics.assert_called_once()
