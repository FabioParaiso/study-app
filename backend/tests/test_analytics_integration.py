import pytest
from unittest.mock import Mock
from io import BytesIO
from modules.materials.deps import get_ai_service as materials_get_ai_service


def _override_material_ai_service(app, topics: dict):
    mock_service = Mock()
    mock_service.is_available.return_value = True
    mock_service.extract_topics.return_value = topics
    app.dependency_overrides[materials_get_ai_service] = lambda: mock_service
    return mock_service

def test_submit_quiz_and_get_analytics(client):
    """Integration test: Submit quiz → Get analytics with weak points."""
    
    # 1. Setup: Register user, upload material
    import time
    name = f"AnalyticsUser{int(time.time()*1000)}"
    register_response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload material (mock AI)
    file_content = b"Test content about Math and Science topics."
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    _override_material_ai_service(client.app, {
        "Math": ["Math"],
        "Science": ["Science"]
    })
    try:
        upload_response = client.post("/upload", files=files, headers=headers)
        assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)
    
    # Get material ID
    material_response = client.get("/current-material", headers=headers)
    material_id = material_response.json()["id"]
    
    # 2. Submit quiz result
    quiz_result = {
        "score": 6,
        "total_questions": 10,
        "quiz_type": "multiple-choice",
        "xp_earned": 50,
        "study_material_id": material_id,
        "detailed_results": [
            {"topic": "Math", "is_correct": True},
            {"topic": "Math", "is_correct": False},
            {"topic": "Science", "is_correct": True},
            {"topic": "Science", "is_correct": True},
            {"topic": "Math", "is_correct": True},
            {"topic": "Science", "is_correct": False},
            {"topic": "Math", "is_correct": False},
            {"topic": "Math", "is_correct": True},
            {"topic": "Science", "is_correct": True},
            {"topic": "Science", "is_correct": True},
        ]
    }
    
    result_response = client.post("/quiz/result", json=quiz_result, headers=headers)
    assert result_response.status_code == 200
    assert result_response.json()["status"] == "saved"
    
    # 3. Get analytics
    analytics_response = client.get(f"/analytics/weak-points?material_id={material_id}", headers=headers)
    assert analytics_response.status_code == 200
    
    analytics = analytics_response.json()
    assert len(analytics) > 0
    
    # Verify analytics structure
    for topic_stat in analytics:
        assert "topic" in topic_stat
        assert "success_rate" in topic_stat
        
    # Verify Math has lower success rate (3/5 with confidence -> 55%)
    math_stat = next(t for t in analytics if t["topic"] == "Math")
    assert math_stat["success_rate"] == 55


def test_adaptive_topics_from_analytics(client):
    """Integration test: Submit multiple quizzes → Get adaptive boost/mastered topics."""
    
    # Setup
    import time
    name = f"AdaptiveUser{int(time.time()*1000)}"
    register_response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload material
    file_content = b"Content about Physics, Chemistry, and Biology."
    files = {"file": ("science.txt", BytesIO(file_content), "text/plain")}
    
    _override_material_ai_service(client.app, {
        "Physics": ["Physics"],
        "Chemistry": ["Chemistry"],
        "Biology": ["Biology"]
    })
    try:
        client.post("/upload", files=files, headers=headers)
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)
    
    material_response = client.get("/current-material", headers=headers)
    material_id = material_response.json()["id"]
    
    # Submit quiz with varied performance
    quiz_result = {
        "score": 8,
        "total_questions": 12,
        "quiz_type": "multiple-choice",
        "xp_earned": 60,
        "study_material_id": material_id,
        "detailed_results": [
            # Physics: 1/3 = 33% (weak)
            {"topic": "Physics", "is_correct": True},
            {"topic": "Physics", "is_correct": False},
            {"topic": "Physics", "is_correct": False},
            # Chemistry: 3/4 = 75% (ok)
            {"topic": "Chemistry", "is_correct": True},
            {"topic": "Chemistry", "is_correct": True},
            {"topic": "Chemistry", "is_correct": False},
            {"topic": "Chemistry", "is_correct": True},
            # Biology: 4/5 = 80% (ok but not mastered)
            {"topic": "Biology", "is_correct": True},
            {"topic": "Biology", "is_correct": True},
            {"topic": "Biology", "is_correct": True},
            {"topic": "Biology", "is_correct": False},
            {"topic": "Biology", "is_correct": True},
        ]
    }
    
    client.post("/quiz/result", json=quiz_result, headers=headers)
    
    # Get analytics to verify adaptive topics logic
    analytics_response = client.get(f"/analytics/weak-points?material_id={material_id}", headers=headers)
    analytics = analytics_response.json()
    
    physics_stat = next(t for t in analytics if t["topic"] == "Physics")
    assert physics_stat["success_rate"] < 70  # Should be in "boost" category


def test_quiz_result_without_material_id_uses_active(client):
    """Integration test: Submit quiz without material_id should use active material."""
    
    import time
    name = f"DefaultMatUser{int(time.time()*1000)}"
    register_response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload material
    files = {"file": ("test.txt", BytesIO(b"Content"), "text/plain")}
    _override_material_ai_service(client.app, {
        "Topic1": ["Topic1"]
    })
    try:
        client.post("/upload", files=files, headers=headers)
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)
    
    # Submit quiz without material_id (should use active)
    quiz_result = {
        "score": 5,
        "total_questions": 5,
        "quiz_type": "multiple-choice",
        "xp_earned": 25,
        "study_material_id": None,  # Explicitly None
        "detailed_results": [
            {"topic": "Topic1", "is_correct": True},
            {"topic": "Topic1", "is_correct": True},
            {"topic": "Topic1", "is_correct": True},
            {"topic": "Topic1", "is_correct": True},
            {"topic": "Topic1", "is_correct": True},
        ]
    }
    
    result_response = client.post("/quiz/result", json=quiz_result, headers=headers)
    assert result_response.status_code == 200


def test_open_ended_score_average_updates_counts(client, db_session):
    """Integration test: open-ended score (average) updates correct_answers_count via normalization."""

    import time
    name = f"OpenScoreUser{int(time.time()*1000)}"
    register_response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    file_content = b"Content about Biology."
    files = {"file": ("bio.txt", BytesIO(file_content), "text/plain")}

    _override_material_ai_service(client.app, {"Biology": ["Biology"]})
    try:
        upload_response = client.post("/upload", files=files, headers=headers)
        assert upload_response.status_code == 200
    finally:
        client.app.dependency_overrides.pop(materials_get_ai_service, None)

    material_response = client.get("/current-material", headers=headers)
    material_id = material_response.json()["id"]

    quiz_result = {
        "score": 70,  # average (0-100)
        "total_questions": 4,
        "quiz_type": "open-ended",
        "xp_earned": 10,
        "study_material_id": material_id,
        "detailed_results": [
            {"topic": "Biology", "is_correct": True},
            {"topic": "Biology", "is_correct": False},
            {"topic": "Biology", "is_correct": True},
            {"topic": "Biology", "is_correct": False},
        ]
    }

    result_response = client.post("/quiz/result", json=quiz_result, headers=headers)
    assert result_response.status_code == 200

    db_session.rollback()
    from models import StudyMaterial
    material = db_session.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    assert material is not None
    # 70% of 4 -> round(2.8) = 3
    assert material.correct_answers_count == 3
