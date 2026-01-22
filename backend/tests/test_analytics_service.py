import pytest
from unittest.mock import Mock
from services.analytics_service import AnalyticsService

class TestAnalyticsService:
    
    @pytest.fixture
    def mock_repo(self):
        """Mock QuizRepository."""
        return Mock()

    @pytest.fixture
    def service(self, mock_repo):
        """Service with mocked repo."""
        return AnalyticsService(mock_repo)

    def test_save_quiz_result_delegates_to_repo(self, service, mock_repo):
        """Test that save_quiz_result calls repo correctly."""
        mock_repo.save_quiz_result.return_value = {"id": 123}
        
        result = service.save_quiz_result(
            student_id=1,
            score=8,
            total=10,
            quiz_type="multiple",
            detailed_results=[{"topic": "Math", "is_correct": True}],
            material_id=5
        )
        
        assert result == {"id": 123}
        mock_repo.save_quiz_result.assert_called_once_with(
            1, 8, 10, "multiple", [{"topic": "Math", "is_correct": True}], 5
        )

    def test_get_weak_points_returns_analytics(self, service, mock_repo):
        """Test get_weak_points delegates to repo."""
        mock_repo.get_student_analytics.return_value = [
            {"topic": "Biology", "success_rate": 50}
        ]
        
        result = service.get_weak_points(student_id=1, material_id=2)
        
        assert result == [{"topic": "Biology", "success_rate": 50}]
        mock_repo.get_student_analytics.assert_called_once_with(1, 2)

    def test_get_adaptive_topics_empty_analytics(self, service, mock_repo):
        """Test adaptive topics when no analytics exist."""
        mock_repo.get_student_analytics.return_value = None
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert result == {"boost": [], "mastered": []}

    def test_get_adaptive_topics_filters_boost_correctly(self, service, mock_repo):
        """Test boost topics (< 70% success rate)."""
        mock_repo.get_student_analytics.return_value = [
            {"topic": "Weak1", "success_rate": 50},
            {"topic": "Weak2", "success_rate": 69},
            {"topic": "OK", "success_rate": 75},
        ]
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert "Weak1" in result["boost"]
        assert "Weak2" in result["boost"]
        assert "OK" not in result["boost"]
        assert len(result["boost"]) == 2

    def test_get_adaptive_topics_filters_mastered_correctly(self, service, mock_repo):
        """Test mastered topics (>= 90% success rate)."""
        mock_repo.get_student_analytics.return_value = [
            {"topic": "Mastered1", "success_rate": 90},
            {"topic": "Mastered2", "success_rate": 100},
            {"topic": "AlmostMastered", "success_rate": 89},
        ]
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert "Mastered1" in result["mastered"]
        assert "Mastered2" in result["mastered"]
        assert "AlmostMastered" not in result["mastered"]
        assert len(result["mastered"]) == 2

    def test_get_adaptive_topics_edge_case_70_percent(self, service, mock_repo):
        """Test topics exactly at 70% are NOT in boost."""
        mock_repo.get_student_analytics.return_value = [
            {"topic": "Exactly70", "success_rate": 70},
        ]
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert "Exactly70" not in result["boost"]
        assert "Exactly70" not in result["mastered"]

    def test_get_adaptive_topics_comprehensive(self, service, mock_repo):
        """Test comprehensive scenario with mixed topics."""
        mock_repo.get_student_analytics.return_value = [
            {"topic": "VeryWeak", "success_rate": 30},
            {"topic": "Weak", "success_rate": 65},
            {"topic": "Average", "success_rate": 75},
            {"topic": "Good", "success_rate": 85},
            {"topic": "Excellent", "success_rate": 95},
        ]
        
        result = service.get_adaptive_topics(student_id=1)
        
        # Boost: < 70
        assert result["boost"] == ["VeryWeak", "Weak"]
        # Mastered: >= 90
        assert result["mastered"] == ["Excellent"]
