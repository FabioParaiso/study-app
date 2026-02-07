import pytest
from unittest.mock import Mock
from io import BytesIO
from datetime import datetime, timedelta, time, timezone
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
        assert "score_data_mcq" in topic_stat
        
    # Verify Math has building state (5 attempts = building)
    math_stat = next(t for t in analytics if t["topic"] == "Math")
    mcq_data = math_stat["score_data_mcq"]
    assert mcq_data["confidence_level"] == "building"
    assert mcq_data["attempts_count"] == 5
    assert "%" in mcq_data["display_value"]  # Should show percentage


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
    mcq_data = physics_stat["score_data_mcq"]
    # Only 3 attempts = exploring state, no score yet
    assert mcq_data["confidence_level"] == "exploring"
    assert mcq_data["attempts_count"] == 3


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
    """Integration test: open-ended correct_answers_count uses per-concept correctness."""

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
    # 2 correct out of 4 concepts
    assert material.correct_answers_count == 2


def test_get_metrics_endpoint_returns_daily_counts(client, db_session):
    import time as time_mod
    name = f"MetricsUser{int(time_mod.time()*1000)}"
    register_response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    student_id = register_response.json()["user"]["id"]

    from models import QuizResult

    today = datetime.now(timezone.utc).date()
    day0 = datetime.combine(today, time(12, 0), tzinfo=timezone.utc)
    day1 = datetime.combine(today - timedelta(days=1), time(12, 0), tzinfo=timezone.utc)

    db_session.add_all([
        QuizResult(
            student_id=student_id,
            study_material_id=None,
            score=5,
            total_questions=10,
            quiz_type="multiple-choice",
            duration_seconds=600,
            active_seconds=500,
            created_at=day0
        ),
        QuizResult(
            student_id=student_id,
            study_material_id=None,
            score=7,
            total_questions=10,
            quiz_type="short_answer",
            duration_seconds=1200,
            active_seconds=1100,
            created_at=day1
        )
    ])
    db_session.commit()

    response = client.get("/analytics/metrics?days=2&tz_offset_minutes=0", headers=headers)
    assert response.status_code == 200

    payload = response.json()
    assert payload["range"]["days"] == 2
    daily = payload["daily"]
    assert len(daily) == 2

    day0_entry = next(d for d in daily if d["day"] == day0.date().isoformat())
    day1_entry = next(d for d in daily if d["day"] == day1.date().isoformat())

    assert day0_entry["tests_total"] == 1
    assert day0_entry["by_type"]["multiple-choice"] == 1
    assert day1_entry["tests_total"] == 1
    assert day1_entry["by_type"]["short_answer"] == 1

    assert payload["totals"]["tests_total"] == 2
    assert payload["totals"]["active_seconds"] == 1600
