from main import app
from unittest.mock import patch, MagicMock

# client comes from conftest


@patch("modules.quizzes.ai_service.QuizAIService.generate_quiz")
@patch("modules.materials.repository.MaterialReadRepository.load")
def test_topic_validation_rejects_invalid_topics_allows_valid(mock_load, mock_generate, client, auth_headers):
    """Validate topic input constraints without exercising LLM schema failures."""
    
    # Mock loaded material
    mock_material = MagicMock()
    mock_material.text = "dummy text"
    mock_material.source = "dummy.pdf"
    mock_material.id = 1
    mock_material.total_xp = 0
    mock_material.topics = []
    mock_load.return_value = mock_material

    # Mock generate to return a dummy list (success)
    mock_generate.return_value = [{
        "question": "q",
        "options": ["o"],
        "correctIndex": 0,
        "explanation": "e",
        "concepts": ["Conceito"]
    }]

    # 1. Test Too Long Topic
    payload = {
        "text": "dummy",
        "use_saved": True,
        "topics": ["A" * 101],
        "quiz_type": "multiple-choice",
        "api_key": "sk-dummy"
        # student_id removed
    }
    response = client.post("/generate-quiz", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "Topic too long" in response.text

    # 2. Test Injection (Newlines)
    payload["topics"] = ["Topic\nNewline"]
    response = client.post("/generate-quiz", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "control characters" in response.text

    # 3. Test Injection (Special Brackets)
    payload["topics"] = ["Topic {Inject}"]
    response = client.post("/generate-quiz", json=payload, headers=auth_headers)
    assert response.status_code == 422
    assert "special brackets" in response.text

    # 4. Valid Topic
    payload["topics"] = ["Revolução Industrial"]
    response = client.post("/generate-quiz", json=payload, headers=auth_headers)
    assert response.status_code == 200
