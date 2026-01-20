from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("main.generate_quiz")
@patch("main.load_study_material")
def test_topic_validation(mock_load, mock_generate):
    """Test the topic validation logic specifically."""
    # Mock loaded material
    mock_load.return_value = {"text": "dummy text", "source": "dummy.pdf"}

    # Mock generate to return a dummy list (success)
    mock_generate.return_value = [{"question": "q", "options": ["o"], "correctIndex": 0, "explanation": "e"}]

    # 1. Test Too Long Topic
    payload = {
        "text": "dummy",
        "use_saved": True,
        "topics": ["A" * 101],
        "quiz_type": "multiple",
        "api_key": "sk-dummy"
    }
    response = client.post("/generate-quiz", json=payload)
    assert response.status_code == 422
    assert "Topic too long" in response.text

    # 2. Test Injection (Newlines)
    payload["topics"] = ["Topic\nNewline"]
    response = client.post("/generate-quiz", json=payload)
    assert response.status_code == 422
    assert "control characters" in response.text

    # 3. Test Injection (Special Brackets)
    payload["topics"] = ["Topic {Inject}"]
    response = client.post("/generate-quiz", json=payload)
    assert response.status_code == 422
    assert "special brackets" in response.text

    # 4. Valid Topic
    payload["topics"] = ["Revolução Industrial"]
    response = client.post("/generate-quiz", json=payload)
    assert response.status_code == 200
