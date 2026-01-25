import pytest
from unittest.mock import Mock
from modules.analytics.service import AnalyticsService

class TestAnalyticsService:
    
    @pytest.fixture
    def analytics_repo(self):
        """Mock AnalyticsRepository."""
        return Mock()

    @pytest.fixture
    def material_repo(self):
        """Mock MaterialRepository."""
        return Mock()

    @pytest.fixture
    def service(self, analytics_repo, material_repo):
        """Service with mocked repos."""
        return AnalyticsService(analytics_repo, material_repo)

    def test_get_weak_points_returns_analytics(self, service, analytics_repo, material_repo):
        """Test get_weak_points aggregates correctly."""
        material_repo.get_concept_pairs.return_value = [("Biology", "Cell")]
        analytics_repo.fetch_question_analytics.return_value = [
            {
                "topic_name": "Biology",
                "concept_name": "Cell",
                "raw_concept": "Cell",
                "is_correct": True
            },
            {
                "topic_name": "Biology",
                "concept_name": "Cell",
                "raw_concept": "Cell",
                "is_correct": False
            }
        ]
        
        result = service.get_weak_points(student_id=1, material_id=2)
        
        assert result == [
            {"topic": "Biology", "concept": "Cell", "success_rate": 50, "total_questions": 2}
        ]
        material_repo.get_concept_pairs.assert_called_once_with(2)
        analytics_repo.fetch_question_analytics.assert_called_once_with(1, 2)

    def test_get_adaptive_topics_empty_analytics(self, service, analytics_repo, material_repo):
        """Test adaptive topics when no analytics exist."""
        material_repo.get_concept_pairs_for_student.return_value = []
        analytics_repo.fetch_question_analytics.return_value = []
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert result == {"boost": [], "mastered": []}

    def test_get_adaptive_topics_filters_boost_correctly(self, service, analytics_repo, material_repo):
        """Test boost topics (< 70% success rate)."""
        material_repo.get_concept_pairs_for_student.return_value = [
            ("Weak1", "C1"),
            ("Weak2", "C2"),
            ("OK", "C3"),
        ]
        analytics_repo.fetch_question_analytics.return_value = [
            {"topic_name": "Weak1", "concept_name": "C1", "raw_concept": "C1", "is_correct": False},
            {"topic_name": "Weak2", "concept_name": "C2", "raw_concept": "C2", "is_correct": False},
            {"topic_name": "Weak2", "concept_name": "C2", "raw_concept": "C2", "is_correct": True},
            {"topic_name": "OK", "concept_name": "C3", "raw_concept": "C3", "is_correct": True},
            {"topic_name": "OK", "concept_name": "C3", "raw_concept": "C3", "is_correct": True},
            {"topic_name": "OK", "concept_name": "C3", "raw_concept": "C3", "is_correct": False},
            {"topic_name": "OK", "concept_name": "C3", "raw_concept": "C3", "is_correct": True},
        ]
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert "Weak1" in result["boost"]
        assert "Weak2" in result["boost"]
        assert "OK" not in result["boost"]
        assert len(result["boost"]) == 2

    def test_get_adaptive_topics_filters_mastered_correctly(self, service, analytics_repo, material_repo):
        """Test mastered topics (>= 90% success rate)."""
        material_repo.get_concept_pairs_for_student.return_value = [
            ("Mastered1", "C1"),
            ("Mastered2", "C2"),
            ("AlmostMastered", "C3"),
        ]
        analytics_repo.fetch_question_analytics.return_value = [
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered1", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Mastered2", "concept_name": "C2", "raw_concept": "C2", "is_correct": True},
            {"topic_name": "AlmostMastered", "concept_name": "C3", "raw_concept": "C3", "is_correct": True},
            {"topic_name": "AlmostMastered", "concept_name": "C3", "raw_concept": "C3", "is_correct": False},
        ]
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert "Mastered1" in result["mastered"]
        assert "Mastered2" in result["mastered"]
        assert "AlmostMastered" not in result["mastered"]
        assert len(result["mastered"]) == 2

    def test_get_adaptive_topics_edge_case_70_percent(self, service, analytics_repo, material_repo):
        """Test topics exactly at 70% are NOT in boost."""
        material_repo.get_concept_pairs_for_student.return_value = [("Exactly70", "C1")]
        analytics_repo.fetch_question_analytics.return_value = [
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": False},
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": False},
            {"topic_name": "Exactly70", "concept_name": "C1", "raw_concept": "C1", "is_correct": False},
        ]
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert "Exactly70" not in result["boost"]
        assert "Exactly70" not in result["mastered"]

    def test_get_adaptive_topics_comprehensive(self, service, analytics_repo, material_repo):
        """Test comprehensive scenario with mixed topics."""
        material_repo.get_concept_pairs_for_student.return_value = [
            ("VeryWeak", "C1"),
            ("Weak", "C2"),
            ("Average", "C3"),
            ("Good", "C4"),
            ("Excellent", "C5"),
        ]
        analytics_repo.fetch_question_analytics.return_value = [
            {"topic_name": "VeryWeak", "concept_name": "C1", "raw_concept": "C1", "is_correct": False},
            {"topic_name": "VeryWeak", "concept_name": "C1", "raw_concept": "C1", "is_correct": False},
            {"topic_name": "VeryWeak", "concept_name": "C1", "raw_concept": "C1", "is_correct": True},
            {"topic_name": "Weak", "concept_name": "C2", "raw_concept": "C2", "is_correct": True},
            {"topic_name": "Weak", "concept_name": "C2", "raw_concept": "C2", "is_correct": False},
            {"topic_name": "Weak", "concept_name": "C2", "raw_concept": "C2", "is_correct": False},
            {"topic_name": "Average", "concept_name": "C3", "raw_concept": "C3", "is_correct": True},
            {"topic_name": "Average", "concept_name": "C3", "raw_concept": "C3", "is_correct": True},
            {"topic_name": "Average", "concept_name": "C3", "raw_concept": "C3", "is_correct": True},
            {"topic_name": "Average", "concept_name": "C3", "raw_concept": "C3", "is_correct": False},
            {"topic_name": "Good", "concept_name": "C4", "raw_concept": "C4", "is_correct": True},
            {"topic_name": "Good", "concept_name": "C4", "raw_concept": "C4", "is_correct": True},
            {"topic_name": "Good", "concept_name": "C4", "raw_concept": "C4", "is_correct": True},
            {"topic_name": "Good", "concept_name": "C4", "raw_concept": "C4", "is_correct": False},
            {"topic_name": "Excellent", "concept_name": "C5", "raw_concept": "C5", "is_correct": True},
            {"topic_name": "Excellent", "concept_name": "C5", "raw_concept": "C5", "is_correct": True},
            {"topic_name": "Excellent", "concept_name": "C5", "raw_concept": "C5", "is_correct": True},
            {"topic_name": "Excellent", "concept_name": "C5", "raw_concept": "C5", "is_correct": True},
        ]
        
        result = service.get_adaptive_topics(student_id=1)
        
        # Boost: < 70
        assert result["boost"] == ["VeryWeak", "Weak"]
        # Mastered: >= 90
        assert result["mastered"] == ["Excellent"]
