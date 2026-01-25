import pytest
from unittest.mock import patch, Mock
from io import BytesIO

def test_submit_quiz_and_get_analytics(client):
    """Integration test: Submit quiz → Get analytics with weak points."""
    
    # 1. Setup: Register user, upload material
    register_response = client.post("/register", json={"name": "AnalyticsUserInt", "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload material (mock AI)
    file_content = b"Test content about Math and Science topics."
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    with patch("modules.materials.router.get_ai_service") as mock_ai:
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.extract_topics.return_value = {
            "Math": ["Math"],
            "Science": ["Science"]
        }
        mock_ai.return_value = mock_service
        client.post("/upload", files=files, headers=headers)
    
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
    register_response = client.post("/register", json={"name": "AdaptiveUserInt", "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload material
    file_content = b"Content about Physics, Chemistry, and Biology."
    files = {"file": ("science.txt", BytesIO(file_content), "text/plain")}
    
    with patch("modules.materials.router.get_ai_service") as mock_ai:
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.extract_topics.return_value = {
            "Physics": ["Physics"],
            "Chemistry": ["Chemistry"],
            "Biology": ["Biology"]
        }
        mock_ai.return_value = mock_service
        client.post("/upload", files=files, headers=headers)
    
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
    
    register_response = client.post("/register", json={"name": "DefaultMatUserInt", "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Upload material
    files = {"file": ("test.txt", BytesIO(b"Content"), "text/plain")}
    with patch("modules.materials.router.get_ai_service") as mock_ai:
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.extract_topics.return_value = {
            "Topic1": ["Topic1"]
        }
        mock_ai.return_value = mock_service
        client.post("/upload", files=files, headers=headers)
    
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
