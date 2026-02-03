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

    # ==================== SCORE DATA TESTS ====================

    def test_get_weak_points_returns_score_data_structure(self, service, analytics_repo, material_repo):
        """Test get_weak_points returns new score_data structure per quiz type."""
        material_repo.get_concept_pairs.return_value = [("Biology", "Cell")]
        analytics_repo.fetch_question_analytics.return_value = [
            {"topic_name": "Biology", "concept_name": "Cell", "is_correct": True, "quiz_type": "multiple-choice"},
            {"topic_name": "Biology", "concept_name": "Cell", "is_correct": False, "quiz_type": "multiple-choice"},
        ]
        
        result = service.get_weak_points(student_id=1, material_id=2)
        
        assert len(result) == 1
        item = result[0]
        
        # Basic fields
        assert item["topic"] == "Biology"
        assert item["concept"] == "Cell"
        assert item["total_questions_mcq"] == 2
        assert item["total_questions_short"] == 0
        assert item["total_questions_bloom"] == 0
        assert item["total_questions"] == 2
        
        # Score data structure for MCQ (2 attempts = exploring)
        mcq_data = item["score_data_mcq"]
        assert mcq_data["confidence_level"] == "exploring"
        assert mcq_data["attempts_count"] == 2
        assert mcq_data["attempts_needed"] == 3  # 5 - 2
        assert mcq_data["display_value"] == "2/5"
        assert mcq_data["score"] is None  # No score in exploring
        
        # Score data for Short and Bloom (not seen)
        assert item["score_data_short"]["confidence_level"] == "not_seen"
        assert item["score_data_bloom"]["confidence_level"] == "not_seen"

    def test_exploring_state_0_to_4_attempts(self, service, analytics_repo, material_repo):
        """Test exploring state with 0-4 attempts shows X/5 format."""
        material_repo.get_concept_pairs.return_value = [("Math", "Algebra")]
        
        # 3 attempts
        analytics_repo.fetch_question_analytics.return_value = [
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"},
        ]
        
        result = service.get_weak_points(student_id=1, material_id=2)
        mcq_data = result[0]["score_data_mcq"]
        
        assert mcq_data["confidence_level"] == "exploring"
        assert mcq_data["display_value"] == "3/5"
        assert mcq_data["attempts_needed"] == 2
        assert mcq_data["score"] is None
        assert mcq_data["status_label"] == "Em Exploração"

    def test_building_state_5_to_6_attempts(self, service, analytics_repo, material_repo):
        """Test building state with 5-6 attempts shows percentage."""
        material_repo.get_concept_pairs.return_value = [("Math", "Algebra")]
        
        # 5 attempts - 4 correct, 1 wrong = 80% mastery
        analytics_repo.fetch_question_analytics.return_value = [
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"},
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": False, "quiz_type": "multiple-choice"},
        ]
        
        result = service.get_weak_points(student_id=1, material_id=2)
        mcq_data = result[0]["score_data_mcq"]
        
        assert mcq_data["confidence_level"] == "building"
        assert mcq_data["display_value"] == "80%"
        assert mcq_data["attempts_needed"] == 2  # 7 - 5
        assert mcq_data["score"] == 0.8
        assert mcq_data["status_label"] == "Promissor"

    def test_established_state_7_plus_attempts(self, service, analytics_repo, material_repo):
        """Test established state with 7+ attempts shows full confidence."""
        material_repo.get_concept_pairs.return_value = [("Math", "Algebra")]
        
        # 7 attempts - all correct = 100%
        analytics_repo.fetch_question_analytics.return_value = [
            {"topic_name": "Math", "concept_name": "Algebra", "is_correct": True, "quiz_type": "multiple-choice"}
            for _ in range(7)
        ]
        
        result = service.get_weak_points(student_id=1, material_id=2)
        mcq_data = result[0]["score_data_mcq"]
        
        assert mcq_data["confidence_level"] == "established"
        assert mcq_data["display_value"] == "100%"
        assert mcq_data["attempts_needed"] == 0
        assert mcq_data["score"] == 1.0
        assert mcq_data["status_label"] == "Forte"

    def test_independent_score_data_per_quiz_type(self, service, analytics_repo, material_repo):
        """Test each quiz type has independent score_data."""
        material_repo.get_concept_pairs.return_value = [("Science", "Physics")]
        
        analytics_repo.fetch_question_analytics.return_value = [
            # MCQ: 7 correct = established, 100%
            *[{"topic_name": "Science", "concept_name": "Physics", "is_correct": True, "quiz_type": "multiple-choice"} for _ in range(7)],
            # Short: 3 attempts = exploring
            *[{"topic_name": "Science", "concept_name": "Physics", "is_correct": True, "quiz_type": "short_answer"} for _ in range(3)],
            # Bloom: 0 = not seen
        ]
        
        result = service.get_weak_points(student_id=1, material_id=2)
        item = result[0]
        
        assert item["score_data_mcq"]["confidence_level"] == "established"
        assert item["score_data_mcq"]["display_value"] == "100%"
        
        assert item["score_data_short"]["confidence_level"] == "exploring"
        assert item["score_data_short"]["display_value"] == "3/5"
        
        assert item["score_data_bloom"]["confidence_level"] == "not_seen"
        assert item["score_data_bloom"]["display_value"] == "--"

    def test_uses_last_7_attempts_for_window(self, service, analytics_repo, material_repo):
        """Test that only last 7 attempts are used for mastery calculation."""
        material_repo.get_concept_pairs.return_value = [("History", "Era")]
        base = datetime(2024, 1, 1)
        
        items = []
        # Old attempts (index 0-2): all wrong
        for i in range(3):
            items.append({
                "topic_name": "History",
                "concept_name": "Era",
                "is_correct": False,
                "quiz_type": "multiple-choice",
                "created_at": base + timedelta(days=i)
            })
        # Recent attempts (index 3-9): all correct
        for i in range(3, 10):
            items.append({
                "topic_name": "History",
                "concept_name": "Era",
                "is_correct": True,
                "quiz_type": "multiple-choice",
                "created_at": base + timedelta(days=i)
            })
        
        analytics_repo.fetch_question_analytics.return_value = items
        
        result = service.get_weak_points(student_id=1, material_id=2)
        mcq_data = result[0]["score_data_mcq"]
        
        # Last 7 should be all correct
        assert mcq_data["confidence_level"] == "established"
        assert mcq_data["score"] == 1.0
        assert mcq_data["status_label"] == "Forte"

    # ==================== ADAPTIVE TOPICS TESTS ====================

    def test_get_adaptive_topics_only_uses_established(self, service, analytics_repo, material_repo):
        """Test adaptive topics only considers established concepts."""
        material_repo.get_concept_pairs_for_student.return_value = [
            ("Weak", "C1"),
            ("Strong", "C2"),
            ("Exploring", "C3"),
        ]
        
        analytics_repo.fetch_question_analytics.return_value = [
            # Weak: 7 correct = 0% -> boost
            *[{"topic_name": "Weak", "concept_name": "C1", "is_correct": False, "quiz_type": "multiple-choice"} for _ in range(7)],
            # Strong: 7 correct = 100% -> mastered
            *[{"topic_name": "Strong", "concept_name": "C2", "is_correct": True, "quiz_type": "multiple-choice"} for _ in range(7)],
            # Exploring: only 3 -> ignored
            *[{"topic_name": "Exploring", "concept_name": "C3", "is_correct": False, "quiz_type": "multiple-choice"} for _ in range(3)],
        ]
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert "Weak" in result["boost"]
        assert "Strong" in result["mastered"]
        assert "Exploring" not in result["boost"]
        assert "Exploring" not in result["mastered"]

    def test_get_adaptive_topics_empty(self, service, analytics_repo, material_repo):
        """Test adaptive topics with no analytics."""
        material_repo.get_concept_pairs_for_student.return_value = []
        analytics_repo.fetch_question_analytics.return_value = []
        
        result = service.get_adaptive_topics(student_id=1)
        
        assert result == {"boost": [], "mastered": []}

    # ==================== CLASSIFIED CONCEPTS TESTS ====================

    def test_get_classified_concepts_uses_score_data(self, service, analytics_repo, material_repo):
        """Test classified concepts uses new score_data structure."""
        material_repo.get_concept_pairs.return_value = [
            ("Topic", "Unseen"),
            ("Topic", "Exploring"),
            ("Topic", "Weak"),
            ("Topic", "Strong"),
        ]
        
        analytics_repo.fetch_question_analytics.return_value = [
            # Unseen: 0 MCQ
            # Exploring: 3 MCQ
            *[{"topic_name": "Topic", "concept_name": "Exploring", "is_correct": True, "quiz_type": "multiple-choice"} for _ in range(3)],
            # Weak: 7 MCQ, 40% = weak
            *[{"topic_name": "Topic", "concept_name": "Weak", "is_correct": i < 3, "quiz_type": "multiple-choice"} for i in range(7)],
            # Strong: 7 MCQ, 100% = strong
            *[{"topic_name": "Topic", "concept_name": "Strong", "is_correct": True, "quiz_type": "multiple-choice"} for _ in range(7)],
        ]
        
        result = service.get_classified_concepts(student_id=1, material_id=2)
        
        assert "Unseen" in result["unseen"]
        assert "Exploring" in result["unseen"]  # Exploring counts as unseen
        assert "Weak" in result["weak"]
        assert "Strong" in result["strong"]

    # ==================== BUILD MCQ QUIZ CONCEPTS ====================

    def test_build_mcq_quiz_concepts_treats_exploring_as_unseen(self, service):
        """Test exploring concepts are treated as unseen for quiz generation."""
        service.get_weak_points = Mock(return_value=[
            {
                "concept": "Unseen",
                "score_data_mcq": {"confidence_level": "not_seen", "score": None},
                "total_questions_mcq": 0,
            },
            {
                "concept": "Exploring",
                "score_data_mcq": {"confidence_level": "exploring", "score": None},
                "total_questions_mcq": 3,
            },
            {
                "concept": "Weak",
                "score_data_mcq": {"confidence_level": "established", "score": 0.4},
                "total_questions_mcq": 10,
            },
            {
                "concept": "Strong",
                "score_data_mcq": {"confidence_level": "established", "score": 0.9},
                "total_questions_mcq": 10,
            },
        ])

        result = service.build_mcq_quiz_concepts(
            student_id=1,
            material_id=2,
            allowed_concepts={"Unseen", "Exploring", "Weak", "Strong"},
            total_questions=10
        )

        assert len(result) == 10
        # Both Unseen and Exploring should be in unseen bucket (5 slots)
        assert result.count("Unseen") + result.count("Exploring") >= 2

    # ==================== LABELS PT-PT ====================

    def test_labels_are_in_portuguese(self, service, analytics_repo, material_repo):
        """Test all labels are in Portuguese."""
        material_repo.get_concept_pairs.return_value = [("T", "C")]
        
        # Test each state
        test_cases = [
            ([], "Não Visto"),  # 0 attempts
            ([True] * 3, "Em Exploração"),  # 3 attempts
            ([True] * 5, "Promissor"),  # 5 correct = 100% building
            ([True] * 7, "Forte"),  # 7 correct = 100% established
            ([True] * 4 + [False] * 3, "Precisa de Prática"),  # 7 attempts, 57% < 65% = needs practice
            ([True] * 5 + [False] * 2, "Bom"),  # 7 attempts, 71% = ok
            ([False] * 7, "Precisa de Prática"),  # 7 wrong = 0% established
        ]
        
        for is_correct_list, expected_label in test_cases:
            analytics_repo.fetch_question_analytics.return_value = [
                {"topic_name": "T", "concept_name": "C", "is_correct": c, "quiz_type": "multiple-choice"}
                for c in is_correct_list
            ]
            result = service.get_weak_points(student_id=1, material_id=2)
            actual_label = result[0]["score_data_mcq"]["status_label"]
            assert actual_label == expected_label, f"Expected '{expected_label}' for {len(is_correct_list)} attempts, got '{actual_label}'"

    # ==================== LEARNING TREND ====================

    def test_get_learning_trend_uses_confidence_window(self, service, analytics_repo):
        """Test learning trend uses CONFIDENCE_WINDOW (7) for calculations."""
        today = datetime.now(timezone.utc).date()
        day_in_range = today - timedelta(days=1)
        day_before_range = today - timedelta(days=3)

        items = []
        base_before = datetime.combine(day_before_range, time(12, 0), tzinfo=timezone.utc)
        # 10 items before range - all correct
        for i in range(10):
            items.append({
                "concept_id": 1,
                "concept_name": "Alpha",
                "is_correct": True,
                "quiz_type": "multiple-choice",
                "created_at": base_before + timedelta(minutes=i)
            })

        base_in_range = datetime.combine(day_in_range, time(12, 0), tzinfo=timezone.utc)
        # 7 items in range - 5 correct, 2 wrong = 71%
        for i in range(7):
            items.append({
                "concept_id": 2,
                "concept_name": "Beta",
                "is_correct": i < 5,
                "quiz_type": "multiple-choice",
                "created_at": base_in_range + timedelta(minutes=i)
            })

        analytics_repo.fetch_question_analytics.return_value = items

        trend = service.get_learning_trend(student_id=1, days=2, tz_offset_minutes=0, min_questions=1)
        daily = trend["daily"]

        day_entry = next(d for d in daily if d["day"] == day_in_range.isoformat())
        
        # Should use window of 7, so Beta should be ~71% (5/7)
        mcq_value = day_entry["by_level"]["multiple-choice"]["value"]
        assert mcq_value is not None
        # Value should be around 85-86% (average of Alpha=100% and Beta=71%)
        assert 80 <= mcq_value <= 90

    # ==================== RECENT METRICS (unchanged) ====================

    def test_get_recent_metrics_aggregates_by_day(self, service, analytics_repo):
        """Test recent metrics aggregation."""
        today = datetime.now(timezone.utc).date()
        day0 = datetime.combine(today, time(12, 0), tzinfo=timezone.utc)
        day1 = datetime.combine(today - timedelta(days=1), time(12, 0), tzinfo=timezone.utc)

        analytics_repo.fetch_quiz_sessions.return_value = [
            {"created_at": day0, "quiz_type": "multiple-choice", "duration_seconds": 600, "active_seconds": 500},
            {"created_at": day0, "quiz_type": "short_answer", "duration_seconds": 1200, "active_seconds": 1100},
            {"created_at": day1, "quiz_type": "open-ended", "duration_seconds": 2000, "active_seconds": 1900}
        ]

        metrics = service.get_recent_metrics(student_id=1, days=2, tz_offset_minutes=0)

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
