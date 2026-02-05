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
        assert item["score_data_short"]["display_value"] == "3/4"
        
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

    def test_mcq_below_threshold_prioritised_by_attempts(self, service):
        """Concepts with fewer attempts are selected before those with more."""
        service.get_weak_points = Mock(return_value=[
            *[{
                "concept": f"Below{i}",
                "score_data_mcq": {"confidence_level": "not_seen", "score": None, "attempts_count": 0},
            } for i in range(6)],
            *[{
                "concept": f"BelowOld{i}",
                "score_data_mcq": {"confidence_level": "exploring", "score": 0.2, "attempts_count": 3},
            } for i in range(6)],
        ])

        result = service.build_mcq_quiz_concepts(student_id=1, total_questions=10)

        assert len(result) == 10
        # All 6 zero-attempt concepts must be present (they have priority)
        for i in range(6):
            assert f"Below{i}" in result

    def test_mcq_max_one_per_concept_when_enough_unique(self, service):
        """No concept appears more than once when there are >= total_questions unique concepts."""
        service.get_weak_points = Mock(return_value=[
            {
                "concept": f"C{i}",
                "score_data_mcq": {"confidence_level": "not_seen", "score": None, "attempts_count": 0},
            }
            for i in range(12)
        ])

        result = service.build_mcq_quiz_concepts(student_id=1, total_questions=10)

        assert len(result) == 10
        assert len(set(result)) == 10  # all unique

    def test_mcq_repetitions_when_few_concepts(self, service):
        """With fewer concepts than slots, round-robin fills to total_questions."""
        service.get_weak_points = Mock(return_value=[
            {"concept": "A", "score_data_mcq": {"confidence_level": "not_seen", "score": None, "attempts_count": 0}},
            {"concept": "B", "score_data_mcq": {"confidence_level": "established", "score": 0.4, "attempts_count": 5}},
            {"concept": "C", "score_data_mcq": {"confidence_level": "established", "score": 0.9, "attempts_count": 10}},
        ])

        result = service.build_mcq_quiz_concepts(student_id=1, total_questions=10)

        assert len(result) == 10
        # Each concept appears at least once
        assert "A" in result
        assert "B" in result
        assert "C" in result
        # Round-robin: 10 / 3 => each appears 3 or 4 times
        for c in ["A", "B", "C"]:
            assert result.count(c) >= 3

    def test_mcq_strong_guaranteed_when_many_below(self, service):
        """At least 1 strong concept even when below-threshold concepts fill all slots."""
        service.get_weak_points = Mock(return_value=[
            *[{
                "concept": f"Below{i}",
                "score_data_mcq": {"confidence_level": "not_seen", "score": None, "attempts_count": 0},
            } for i in range(15)],
            {
                "concept": "Strong1",
                "score_data_mcq": {"confidence_level": "established", "score": 0.95, "attempts_count": 20},
            },
        ])

        result = service.build_mcq_quiz_concepts(student_id=1, total_questions=10)

        assert len(result) == 10
        assert "Strong1" in result

    def test_mcq_weak_guaranteed_when_many_below(self, service):
        """At least 1 weak concept even when below-threshold would fill remaining slots."""
        below = [{
            "concept": f"Below{i}",
            "score_data_mcq": {"confidence_level": "not_seen", "score": None, "attempts_count": 0},
        } for i in range(12)]
        weak = [{
            "concept": f"Weak{i}",
            "score_data_mcq": {"confidence_level": "established", "score": 0.5, "attempts_count": 8},
        } for i in range(8)]
        service.get_weak_points = Mock(return_value=below + weak)

        result = service.build_mcq_quiz_concepts(student_id=1, total_questions=10)

        assert len(result) == 10
        weak_in_result = [c for c in result if c.startswith("Weak")]
        assert len(weak_in_result) >= 1

    def test_mcq_all_below_fills_quiz(self, service):
        """When only below-threshold concepts exist, the quiz is still filled."""
        service.get_weak_points = Mock(return_value=[
            {
                "concept": f"Below{i}",
                "score_data_mcq": {"confidence_level": "not_seen", "score": None, "attempts_count": i},
            }
            for i in range(5)
        ])

        result = service.build_mcq_quiz_concepts(student_id=1, total_questions=10)

        assert len(result) == 10
        # All 5 concepts must appear (round-robin)
        for i in range(5):
            assert f"Below{i}" in result

    def test_mcq_no_below_weak_plus_strong(self, service):
        """With 0 below-threshold, weak and strong fill quiz correctly."""
        service.get_weak_points = Mock(return_value=[
            *[{
                "concept": f"Weak{i}",
                "score_data_mcq": {"confidence_level": "established", "score": 0.3 + i * 0.05, "attempts_count": 10},
            } for i in range(7)],
            *[{
                "concept": f"Strong{i}",
                "score_data_mcq": {"confidence_level": "established", "score": 0.85 + i * 0.02, "attempts_count": 15},
            } for i in range(5)],
        ])

        result = service.build_mcq_quiz_concepts(student_id=1, total_questions=10)

        assert len(result) == 10
        assert len(set(result)) == 10  # all unique
        # All 7 weak should be present (priority over strong)
        for i in range(7):
            assert f"Weak{i}" in result
        # 3 strong fill remaining slots
        strong_in_result = [c for c in result if c.startswith("Strong")]
        assert len(strong_in_result) == 3

    # ==================== CHECK SHORT ANSWER READINESS ====================

    def test_short_readiness_all_concepts_confident(self, service):
        """Ready when all concepts have building/established MCQ confidence."""
        service.get_weak_points = Mock(return_value=[
            {"concept": "A", "score_data_mcq": {"confidence_level": "established", "score": 0.8, "attempts_count": 7}},
            {"concept": "B", "score_data_mcq": {"confidence_level": "building", "score": 0.6, "attempts_count": 5}},
        ])
        result = service.check_short_answer_readiness(student_id=1)
        assert result["is_ready"] is True
        assert result["ready_concepts"] == 2
        assert result["total_concepts"] == 2

    def test_short_readiness_not_ready_when_exploring(self, service):
        """Not ready when some concepts are still exploring."""
        service.get_weak_points = Mock(return_value=[
            {"concept": "A", "score_data_mcq": {"confidence_level": "established", "score": 0.9, "attempts_count": 10}},
            {"concept": "B", "score_data_mcq": {"confidence_level": "exploring", "score": None, "attempts_count": 3}},
            {"concept": "C", "score_data_mcq": {"confidence_level": "not_seen", "score": None, "attempts_count": 0}},
        ])
        result = service.check_short_answer_readiness(student_id=1)
        assert result["is_ready"] is False
        assert result["ready_concepts"] == 1
        assert result["total_concepts"] == 3

    def test_short_readiness_not_ready_when_empty(self, service):
        """Not ready when there are no concepts."""
        service.get_weak_points = Mock(return_value=[])
        result = service.check_short_answer_readiness(student_id=1)
        assert result["is_ready"] is False
        assert result["total_concepts"] == 0

    # ==================== BUILD SHORT QUIZ CONCEPTS ====================

    def _make_short_item(self, concept, mcq_score, mcq_conf="established",
                         short_score=0, short_conf="not_seen", short_attempts=0):
        """Helper to build a concept item with MCQ and Short data."""
        return {
            "concept": concept,
            "score_data_mcq": {
                "confidence_level": mcq_conf,
                "score": mcq_score / 100,
                "attempts_count": 7 if mcq_conf == "established" else 5,
            },
            "score_data_short": {
                "confidence_level": short_conf,
                "score": short_score / 100 if short_score else None,
                "attempts_count": short_attempts,
            },
        }

    def test_short_bucket_a_weak_mcq_prioritised(self, service):
        """Concepts with MCQ <= 75% go to bucket A (weak) and are prioritised."""
        service.get_weak_points = Mock(return_value=[
            self._make_short_item("Weak1", mcq_score=50),
            self._make_short_item("Weak2", mcq_score=60),
            self._make_short_item("Weak3", mcq_score=40),
            self._make_short_item("Strong1", mcq_score=90),
            self._make_short_item("Strong2", mcq_score=85),
            self._make_short_item("Strong3", mcq_score=95),
        ])
        result = service.build_short_quiz_concepts(student_id=1, total_questions=8)

        assert len(result) == 8
        # All 3 weak concepts must appear (bucket A quota = 3)
        assert "Weak1" in result
        assert "Weak2" in result
        assert "Weak3" in result

    def test_short_bucket_classification(self, service):
        """Concepts are correctly classified into A/B/C buckets."""
        service.get_weak_points = Mock(return_value=[
            # Bucket A: MCQ weak
            self._make_short_item("WeakConcept", mcq_score=60),
            # Bucket B: MCQ strong, short not mastered
            self._make_short_item("ArticulateConcept", mcq_score=90, short_score=40, short_conf="building", short_attempts=5),
            # Bucket C: MCQ strong, short strong
            self._make_short_item("MasteredConcept", mcq_score=95, short_score=85, short_conf="established", short_attempts=7),
        ])
        result = service.build_short_quiz_concepts(student_id=1, total_questions=8)

        assert len(result) == 8
        assert "WeakConcept" in result
        assert "ArticulateConcept" in result
        assert "MasteredConcept" in result
        # Weak concept should repeat more (expansion from bucket A)
        assert result.count("WeakConcept") >= 2

    def test_short_quotas_with_many_concepts(self, service):
        """With many concepts, quotas limit each bucket (3A + 2B + 1C = 6 unique)."""
        items = (
            [self._make_short_item(f"Weak{i}", mcq_score=40 + i * 5) for i in range(8)]
            + [self._make_short_item(f"Art{i}", mcq_score=80 + i) for i in range(5)]
            + [self._make_short_item(f"Mast{i}", mcq_score=90 + i, short_score=80 + i, short_conf="established", short_attempts=7) for i in range(3)]
        )
        service.get_weak_points = Mock(return_value=items)
        result = service.build_short_quiz_concepts(student_id=1, total_questions=8)

        assert len(result) == 8
        unique = set(result)
        assert len(unique) == 6  # target 6 unique

        weak_in = [c for c in unique if c.startswith("Weak")]
        art_in = [c for c in unique if c.startswith("Art")]
        mast_in = [c for c in unique if c.startswith("Mast")]
        assert len(weak_in) == 3   # quota A
        assert len(art_in) == 2    # quota B
        assert len(mast_in) == 1   # quota C

    def test_short_cascade_when_bucket_empty(self, service):
        """When bucket A is empty, slots cascade to B then C."""
        items = [
            # No weak concepts — all MCQ strong
            self._make_short_item(f"Art{i}", mcq_score=80 + i) for i in range(4)
        ] + [
            self._make_short_item(f"Mast{i}", mcq_score=90 + i, short_score=85, short_conf="established", short_attempts=7) for i in range(3)
        ]
        service.get_weak_points = Mock(return_value=items)
        result = service.build_short_quiz_concepts(student_id=1, total_questions=8)

        assert len(result) == 8
        # All 4 articulate + some mastered should fill the 6 unique slots
        for i in range(4):
            assert f"Art{i}" in result

    def test_short_repetitions_from_weak(self, service):
        """Expansion to 8 questions repeats concepts from bucket A."""
        service.get_weak_points = Mock(return_value=[
            self._make_short_item("W1", mcq_score=50),
            self._make_short_item("W2", mcq_score=60),
            self._make_short_item("W3", mcq_score=70),
            self._make_short_item("A1", mcq_score=85),
            self._make_short_item("A2", mcq_score=90),
            self._make_short_item("M1", mcq_score=95, short_score=85, short_conf="established", short_attempts=7),
        ])
        result = service.build_short_quiz_concepts(student_id=1, total_questions=8)

        assert len(result) == 8
        unique = set(result)
        assert len(unique) == 6
        # 2 extra slots should come from weak concepts (W1, W2, W3)
        weak_counts = sum(1 for c in result if c.startswith("W"))
        assert weak_counts >= 4  # 3 unique + at least 1 repetition

    def test_short_few_concepts_round_robin(self, service):
        """With fewer than 6 concepts, all are used and repeated."""
        service.get_weak_points = Mock(return_value=[
            self._make_short_item("Only1", mcq_score=50),
            self._make_short_item("Only2", mcq_score=85),
        ])
        result = service.build_short_quiz_concepts(student_id=1, total_questions=8)

        assert len(result) == 8
        assert "Only1" in result
        assert "Only2" in result
        # Both concepts should repeat to fill 8 slots
        assert result.count("Only1") >= 2
        assert result.count("Only2") >= 2

    def test_short_empty_returns_empty(self, service):
        """Returns empty list when no concepts exist."""
        service.get_weak_points = Mock(return_value=[])
        result = service.build_short_quiz_concepts(student_id=1, total_questions=8)
        assert result == []

    def test_short_all_mastered_still_fills_quiz(self, service):
        """When all concepts are mastered (C), quiz still fills correctly."""
        items = [
            self._make_short_item(f"M{i}", mcq_score=90 + i, short_score=80 + i, short_conf="established", short_attempts=7)
            for i in range(10)
        ]
        service.get_weak_points = Mock(return_value=items)
        result = service.build_short_quiz_concepts(student_id=1, total_questions=8)

        assert len(result) == 8
        # Should still select 6 unique and expand to 8
        assert len(set(result)) == 6

    def test_short_weak_sorted_by_mcq_desc(self, service):
        """Within bucket A, concepts are sorted by MCQ score descending (moderately weak first)."""
        service.get_weak_points = Mock(return_value=[
            self._make_short_item("VeryWeak", mcq_score=20),
            self._make_short_item("ModerateWeak", mcq_score=70),
            self._make_short_item("MildWeak", mcq_score=75),
            self._make_short_item("Strong", mcq_score=90),
        ])
        # With quota A=3 and only 4 concepts, all 3 weak selected
        result = service.build_short_quiz_concepts(student_id=1, total_questions=8)

        assert "ModerateWeak" in result
        assert "MildWeak" in result
        assert "VeryWeak" in result

    def test_short_respects_allowed_concepts(self, service):
        """Only concepts in allowed_concepts set are considered."""
        service.get_weak_points = Mock(return_value=[
            self._make_short_item("Allowed1", mcq_score=50),
            self._make_short_item("Excluded", mcq_score=60),
            self._make_short_item("Allowed2", mcq_score=85),
        ])
        result = service.build_short_quiz_concepts(
            student_id=1,
            allowed_concepts={"Allowed1", "Allowed2"},
            total_questions=8
        )

        assert "Allowed1" in result
        assert "Allowed2" in result
        assert "Excluded" not in result

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
