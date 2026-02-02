import pytest
from datetime import datetime, timedelta, time, timezone
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
                "is_correct": True,
                "quiz_type": "multiple-choice"
            },
            {
                "topic_name": "Biology",
                "concept_name": "Cell",
                "raw_concept": "Cell",
                "is_correct": False,
                "quiz_type": "multiple-choice"
            }
        ]
        
        result = service.get_weak_points(student_id=1, material_id=2)
        
        assert result == [
            {
                "topic": "Biology",
                "concept": "Cell",
                "success_rate": 50,
                "total_questions_mcq": 2,
                "total_questions_short": 0,
                "total_questions_bloom": 0,
                "total_questions": 2,
                "mastery_raw": 50,
                "status": "Em aprendizagem",
                "effective_mcq": 50,
                "effective_short": 0,
                "effective_bloom": 0,
            }
        ]
        material_repo.get_concept_pairs.assert_called_once_with(2)
        analytics_repo.fetch_question_analytics.assert_called_once_with(1, 2)

    def test_get_weak_points_uses_last_10_by_created_at(self, service, analytics_repo, material_repo):
        """Test analytics uses the last 10 attempts per concept (by created_at)."""
        material_repo.get_concept_pairs.return_value = [("History", "Era")]
        base = datetime(2024, 1, 1)
        items = [
            {
                "topic_name": "History",
                "concept_name": "Era",
                "raw_concept": "Era",
                "is_correct": False,
                "created_at": base,
            },
            {
                "topic_name": "History",
                "concept_name": "Era",
                "raw_concept": "Era",
                "is_correct": False,
                "created_at": base + timedelta(days=1),
            },
        ]
        for offset in range(2, 12):
            items.append({
                "topic_name": "History",
                "concept_name": "Era",
                "raw_concept": "Era",
                "is_correct": True,
                "created_at": base + timedelta(days=offset),
            })

        analytics_repo.fetch_question_analytics.return_value = items

        result = service.get_weak_points(student_id=1, material_id=2)

        assert len(result) == 1
        stat = result[0]
        assert stat["success_rate"] == 100
        assert stat["mastery_raw"] == 100
        assert stat["total_questions"] == 12
        assert stat["status"] == "Forte"

    def test_get_weak_points_includes_mastery_raw_for_unseen(self, service, analytics_repo, material_repo):
        """Test mastery_raw is present when there are no attempts."""
        material_repo.get_concept_pairs.return_value = [("Art", "Color")]
        analytics_repo.fetch_question_analytics.return_value = []

        result = service.get_weak_points(student_id=1, material_id=2)

        assert len(result) == 1
        stat = result[0]
        assert stat["topic"] == "Art"
        assert stat["concept"] == "Color"
        assert stat["success_rate"] == 0
        assert stat["total_questions"] == 0
        assert stat["mastery_raw"] == 0
        assert "status" in stat

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
        assert "OK" in result["boost"]
        assert len(result["boost"]) == 3

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
        assert "Mastered2" not in result["mastered"]
        assert "AlmostMastered" not in result["mastered"]
        assert len(result["mastered"]) == 1

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
        assert result["boost"] == ["Average", "Good", "VeryWeak", "Weak"]
        # Mastered: >= 90
        assert result["mastered"] == []

    def test_get_weak_points_calculates_split_metrics(self, service, analytics_repo, material_repo):
        """Test effective metrics are calculated separately by quiz_type."""
        material_repo.get_concept_pairs.return_value = [("Math", "Algebra")]
        analytics_repo.fetch_question_analytics.return_value = [
            # MCQ: 2 Correct, 2 Incorrect (Total 4) -> 50% Mastery
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": False, "quiz_type": "multiple-choice"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": False, "quiz_type": "multiple-choice"},
            
            # Short: 3 Correct (Total 3) -> 100% Mastery
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "short_answer"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "short_answer"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "short_answer"},

            # Bloom: 1 Incorrect (Total 1) -> 0% Mastery
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": False, "quiz_type": "open-ended"},
        ]
        
        result = service.get_weak_points(student_id=1, material_id=2)
        
        stat = result[0]
        
        # Calculations:
        # MCQ (4 items): Conf=0.4. Eff = 0.5*0.4 + 0.5*0.6 = 0.2 + 0.3 = 0.5 -> 50%
        assert stat["effective_mcq"] == 50
        
        # Short (3 items): Conf=0.3. Eff = 1.0*0.3 + 0.5*0.7 = 0.3 + 0.35 = 0.65 -> 65%
        assert stat["effective_short"] == 65
        
        # Bloom (1 item): Conf=0.1. Eff = 0.0*0.1 + 0.5*0.9 = 0.0 + 0.45 = 0.45 -> 45%
        assert stat["effective_bloom"] == 45

    def test_build_mcq_quiz_concepts_prioritizes_worst_weak(self, service):
        """Test MCQ concept list fills quotas and prioritizes weaker concepts."""
        service.get_weak_points = Mock(return_value=[
            {"concept": "Unseen", "effective_mcq": 0, "total_questions_mcq": 0},
            {"concept": "Weak5", "effective_mcq": 5, "total_questions_mcq": 10},
            {"concept": "Weak20", "effective_mcq": 20, "total_questions_mcq": 10},
            {"concept": "Strong", "effective_mcq": 90, "total_questions_mcq": 10},
        ])

        result = service.build_mcq_quiz_concepts(
            student_id=1,
            material_id=2,
            allowed_concepts={"Unseen", "Weak5", "Weak20", "Strong"},
            total_questions=10
        )

        assert len(result) == 10
        assert result.count("Unseen") == 5
        assert result.count("Strong") == 1
        assert result.count("Weak5") + result.count("Weak20") == 4
        assert result.count("Weak5") > result.count("Weak20")

    def test_get_recent_metrics_aggregates_by_day(self, service, analytics_repo):
        today = datetime.now(timezone.utc).date()
        day0 = datetime.combine(today, time(12, 0), tzinfo=timezone.utc)
        day1 = datetime.combine(today - timedelta(days=1), time(12, 0), tzinfo=timezone.utc)

        analytics_repo.fetch_quiz_sessions.return_value = [
            {
                "created_at": day0,
                "quiz_type": "multiple-choice",
                "duration_seconds": 600,
                "active_seconds": 500
            },
            {
                "created_at": day0,
                "quiz_type": "short_answer",
                "duration_seconds": 1200,
                "active_seconds": 1100
            },
            {
                "created_at": day1,
                "quiz_type": "open-ended",
                "duration_seconds": 2000,
                "active_seconds": 1900
            }
        ]

        metrics = service.get_recent_metrics(student_id=1, days=2, tz_offset_minutes=0)

        analytics_repo.fetch_quiz_sessions.assert_called_once()
        daily = metrics["daily"]
        assert len(daily) == 2

        day0_entry = next(d for d in daily if d["day"] == day0.date().isoformat())
        day1_entry = next(d for d in daily if d["day"] == day1.date().isoformat())

        assert day0_entry["tests_total"] == 2
        assert day0_entry["by_type"]["multiple-choice"] == 1
        assert day0_entry["by_type"]["short_answer"] == 1
        assert day0_entry["active_seconds"] == 1600

        assert day1_entry["tests_total"] == 1
        assert day1_entry["by_type"]["open-ended"] == 1

        assert metrics["totals"]["tests_total"] == 3
        assert metrics["totals"]["active_seconds"] == 3500

    def test_get_learning_trend_accumulates_and_gates_by_min_questions(self, service, analytics_repo):
        today = datetime.now(timezone.utc).date()
        day_in_range = today - timedelta(days=1)
        day_before_range = today - timedelta(days=3)

        items = []
        base_before = datetime.combine(day_before_range, time(12, 0), tzinfo=timezone.utc)
        for i in range(10):
            items.append({
                "concept_id": 1,
                "concept_name": "Alpha",
                "raw_concept": "Alpha",
                "is_correct": i < 9,
                "quiz_type": "multiple-choice",
                "created_at": base_before + timedelta(minutes=i)
            })

        base_in_range = datetime.combine(day_in_range, time(12, 0), tzinfo=timezone.utc)
        for i in range(10):
            items.append({
                "concept_id": 2,
                "concept_name": "Beta",
                "raw_concept": "Beta",
                "is_correct": i < 5,
                "quiz_type": "multiple-choice",
                "created_at": base_in_range + timedelta(minutes=i)
            })

        analytics_repo.fetch_question_analytics.return_value = items

        trend = service.get_learning_trend(student_id=1, days=2, tz_offset_minutes=0, min_questions=1)
        daily = trend["daily"]

        day_entry = next(d for d in daily if d["day"] == day_in_range.isoformat())
        today_entry = next(d for d in daily if d["day"] == today.isoformat())

        assert day_entry["by_level"]["multiple-choice"]["value"] == 70
        assert day_entry["by_level"]["multiple-choice"]["questions"] == 10
        assert today_entry["by_level"]["multiple-choice"]["value"] is None
