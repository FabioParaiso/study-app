import pytest
from unittest.mock import Mock
from io import BytesIO
import time
from models import StudyMaterial
from modules.materials.deps import get_ai_service as materials_get_ai_service
from modules.quizzes.router import get_quiz_ai_service, get_eval_ai_service


def _override_material_ai_service(app, topics: dict):
    mock_service = Mock()
    mock_service.is_available.return_value = True
    mock_service.extract_topics.return_value = topics
    app.dependency_overrides[materials_get_ai_service] = lambda: mock_service
    return mock_service


def _override_quiz_ai_service(app, questions: list[dict]):
    mock_service = Mock()
    mock_service.is_available.return_value = True
    mock_service.generate_quiz.return_value = questions
    app.dependency_overrides[get_quiz_ai_service] = lambda: mock_service
    app.dependency_overrides[get_eval_ai_service] = lambda: mock_service
    return mock_service



def test_upload_and_generate_quiz_flow(client):
    """Integration test: Upload file → Generate Quiz (mocked AI)."""
    
    # 1. Register and get token (use unique numeric suffix)
    unique_name = f"IntegUser{int(time.time()*100)}"
    register_response = client.post("/register", json={"name": unique_name, "password": "StrongPass1!"})
    assert register_response.status_code == 200, f"Register failed: {register_response.text}"
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Upload a text file
    file_content = b"Photosynthesis is the process by which plants convert light into energy."
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    # Mock AI service for topic extraction
    _override_material_ai_service(client.app, {
        "Photosynthesis": ["Photosynthesis"],
        "Biology": ["Biology"]
    })
    try:
        upload_response = client.post("/upload", files=files, headers=headers)
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)
    
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert "text" in upload_data
    assert "Photosynthesis" in upload_data["text"]
    
    # 3. Verify material was saved
    material_response = client.get("/current-material", headers=headers)
    assert material_response.status_code == 200
    material_data = material_response.json()
    assert material_data["has_material"] is True
    assert "test.txt" in material_data["source"]
    
    # 4. Generate Quiz (mock AI quiz generation)
    _override_quiz_ai_service(client.app, [
        {
            "topic": "Photosynthesis",
            "concepts": ["Photosynthesis"],
            "question": "What is photosynthesis?",
            "options": ["A", "B", "C", "D"],
            "correctIndex": 0,
            "explanation": "Test explanation"
        }
    ])
    try:
        quiz_request = {
            "topics": [],
            "quiz_type": "multiple-choice",
            "api_key": "sk-test"
        }
        quiz_response = client.post("/generate-quiz", json=quiz_request, headers=headers)
    finally:
        client.app.dependency_overrides.pop(get_quiz_ai_service, None)
        client.app.dependency_overrides.pop(get_eval_ai_service, None)
    
    assert quiz_response.status_code == 200
    quiz_data = quiz_response.json()
    assert "questions" in quiz_data
    assert len(quiz_data["questions"]) == 1
    assert quiz_data["questions"][0]["topic"] == "Photosynthesis"


def test_generate_open_ended_quiz(client, db_session):
    """Integration test: Generate Open Ended quiz (verifying strategies)."""
    
    # Register & Login
    unique_name = f"OpenEnded{int(time.time()*100)}"
    register_response = client.post("/register", json={"name": unique_name, "password": "StrongPass1!"})
    assert register_response.status_code == 200
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload material (fake content)
    files = {"file": ("test.txt", BytesIO(b"Data about History."), "text/plain")}
    # Mock upload AI to avoid failure
    _override_material_ai_service(client.app, {
        "History": ["History"]
    })
    try:
        client.post("/upload", files=files, headers=headers)
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)

    # Force material XP to 1000 directly in DB
    material_response = client.get("/current-material", headers=headers)
    material_id = material_response.json()["id"]
    db_session.rollback()
    material = db_session.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    assert material is not None
    material.total_xp = 1000
    db_session.commit()

    # Generate Quiz (mock AI quiz generation)
    _override_quiz_ai_service(client.app, [
        {"question": "Explain the causes of WWII.", "topic": "History", "concepts": ["History"]}
    ])
    try:
        quiz_request = {
            "topics": [],
            "quiz_type": "open-ended",
            "api_key": "sk-test"
        }
        quiz_response = client.post("/generate-quiz", json=quiz_request, headers=headers)
    finally:
        client.app.dependency_overrides.pop(get_quiz_ai_service, None)
        client.app.dependency_overrides.pop(get_eval_ai_service, None)

    assert quiz_response.status_code == 200
    quiz_data = quiz_response.json()
    assert "questions" in quiz_data
    assert len(quiz_data["questions"]) == 1
    assert quiz_data["questions"][0]["topic"] == "History"


def test_generate_quiz_shuffles_correct_index(client):
    """Integration test: shuffled options keep correctIndex consistent."""
    unique_name = f"ShuffleUser{int(time.time()*100)}"
    register_response = client.post("/register", json={"name": unique_name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("test.txt", BytesIO(b"Data."), "text/plain")}
    _override_material_ai_service(client.app, {"Topic": ["Topic"]})
    try:
        client.post("/upload", files=files, headers=headers)
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)

    questions = [
        {
            "topic": "Topic",
            "concepts": ["Topic"],
            "question": "Q",
            "options": ["A", "B", "C", "D"],
            "correctIndex": 0,
            "explanation": "E"
        }
    ]
    _override_quiz_ai_service(client.app, questions)
    try:
        quiz_request = {
            "topics": [],
            "quiz_type": "multiple-choice",
            "api_key": "sk-test"
        }
        quiz_response = client.post("/generate-quiz", json=quiz_request, headers=headers)
    finally:
        client.app.dependency_overrides.pop(get_quiz_ai_service, None)
        client.app.dependency_overrides.pop(get_eval_ai_service, None)

    assert quiz_response.status_code == 200
    returned = quiz_response.json()["questions"][0]
    assert returned["options"][returned["correctIndex"]] == "A"


def test_evaluate_answer_open_ended(client):
    """Integration test: evaluate-answer returns evaluation payload."""
    unique_name = f"EvalUser{int(time.time()*100)}"
    register_response = client.post("/register", json={"name": unique_name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("test.txt", BytesIO(b"Context text."), "text/plain")}
    _override_material_ai_service(client.app, {"Topic": ["Topic"]})
    try:
        client.post("/upload", files=files, headers=headers)
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)

    # Mock evaluation AI
    mock_service = Mock()
    mock_service.is_available.return_value = True
    mock_service.evaluate_answer.return_value = {"score": 80, "feedback": "Good"}
    client.app.dependency_overrides[get_eval_ai_service] = lambda: mock_service
    try:
        payload = {"question": "Q", "user_answer": "A", "quiz_type": "open-ended"}
        response = client.post("/evaluate-answer", json=payload, headers=headers)
    finally:
        client.app.dependency_overrides.pop(get_eval_ai_service, None)

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 80
    assert "feedback" in data


def test_evaluate_answer_short_answer(client):
    """Integration test: evaluate-answer short_answer returns evaluation payload."""
    unique_name = f"EvalShort{int(time.time()*100)}"
    register_response = client.post("/register", json={"name": unique_name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("test.txt", BytesIO(b"Context text."), "text/plain")}
    _override_material_ai_service(client.app, {"Topic": ["Topic"]})
    try:
        client.post("/upload", files=files, headers=headers)
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)

    mock_service = Mock()
    mock_service.is_available.return_value = True
    mock_service.evaluate_answer.return_value = {"score": 60, "feedback": "Ok"}
    client.app.dependency_overrides[get_eval_ai_service] = lambda: mock_service
    try:
        payload = {"question": "Q", "user_answer": "A", "quiz_type": "short_answer"}
        response = client.post("/evaluate-answer", json=payload, headers=headers)
    finally:
        client.app.dependency_overrides.pop(get_eval_ai_service, None)

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 60
    assert "feedback" in data


def test_generate_short_answer_quiz_locked(client):
    """Integration test: Verify Short Answer is locked for low XP users."""
    
    # Register (0 XP initially)
    unique_name = f"LowXP{int(time.time()*100)}"
    register_response = client.post("/register", json={"name": unique_name, "password": "StrongPass1!"})
    assert register_response.status_code == 200
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload material
    files = {"file": ("test.txt", BytesIO(b"Data."), "text/plain")}
    _override_material_ai_service(client.app, {
        "Topic": ["Topic"]
    })
    try:
        client.post("/upload", files=files, headers=headers)
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)
         
    # Generate Short Answer (Requires 300 XP)
    quiz_request = {
        "topics": [],
        "quiz_type": "short_answer",
        "api_key": "sk-test"
    }
    quiz_response = client.post("/generate-quiz", json=quiz_request, headers=headers)
    
    # Should be Forbidden (403)
    assert quiz_response.status_code == 403
    assert "Level Locked" in quiz_response.json()["detail"]


def test_upload_file_size_limit(client):
    """Integration test: Verify file size limit enforcement (10MB)."""
    
    name = f"SizeTest{int(time.time()*100)}"
    register_response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a file >10MB
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large.txt", BytesIO(large_content), "text/plain")}
    
    upload_response = client.post("/upload", files=files, headers=headers)
    
    assert upload_response.status_code == 413
    assert "File too large" in upload_response.json()["detail"]


def test_generate_quiz_without_material(client):
    """Integration test: Generate quiz before uploading material should fail."""
    
    name = f"NoMat{int(time.time()*100)}"
    register_response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    quiz_request = {
        "topics": [],
        "quiz_type": "multiple-choice",
        "api_key": "sk-test"
    }
    quiz_response = client.post("/generate-quiz", json=quiz_request, headers=headers)
    
    assert quiz_response.status_code == 400
    assert "No material found" in quiz_response.json()["detail"]
