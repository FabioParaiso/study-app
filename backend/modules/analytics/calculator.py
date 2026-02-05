from typing import Iterable
from datetime import datetime
from modules.analytics.constants import QUIZ_TYPES, CONFIDENCE_WINDOW, EXPLORING_THRESHOLD_MCQ, EXPLORING_THRESHOLD_SHORT, EXPLORING_THRESHOLD_BLOOM


def _get_building_status(mastery: float) -> tuple[str, str]:
    """Labels para estado 'building' (PT-PT)."""
    if mastery >= 0.8:
        return ("promising", "Promissor")
    elif mastery >= 0.65:
        return ("progressing", "Em Progresso")
    else:
        return ("still_learning", "Ainda a Aprender")


def _get_established_status(mastery: float) -> tuple[str, str]:
    """Labels para estado 'established' (PT-PT)."""
    if mastery >= 0.8:
        return ("strong", "Forte")
    elif mastery >= 0.65:
        return ("ok", "Bom")
    else:
        return ("needs_practice", "Precisa de Prática")


def _calculate_mastery_simple(items: list[dict], window_size: int = 7) -> float:
    """
    Simple mastery calculation for learning trend.
    Returns mastery score 0.0-1.0 based on last N items.
    """
    if not items:
        return 0.0
    
    window = items[:window_size]
    if not window:
        return 0.0
    
    correct = sum(1 for i in window if i.get("is_correct"))
    return correct / len(window)


class AnalyticsCalculator:
    @staticmethod
    def _calculate_score_data(items: list[dict], exploring_threshold: int = EXPLORING_THRESHOLD_MCQ) -> dict:
        """
        Calculates score data with gradual confidence levels.
        
        Returns dict with:
        - score: float | None (None if exploring)
        - confidence_level: "not_seen" | "exploring" | "building" | "established"
        - attempts_count: int
        - attempts_needed: int
        - display_value: str ("--", "X/5", or "XX%")
        - status_key: str
        - status_label: str (PT-PT)
        """
        count = len(items) if items else 0
        
        # State: Not seen
        if count == 0:
            return {
                "score": None,
                "confidence_level": "not_seen",
                "attempts_count": 0,
                "attempts_needed": exploring_threshold,
                "display_value": "--",
                "status_key": "not_seen",
                "status_label": "Não Visto"
            }

        window = items[:CONFIDENCE_WINDOW]
        actual_count = len(window)

        # State: Exploring
        if actual_count < exploring_threshold:
            return {
                "score": None,
                "confidence_level": "exploring",
                "attempts_count": actual_count,
                "attempts_needed": exploring_threshold - actual_count,
                "display_value": f"{actual_count}/{exploring_threshold}",
                "status_key": "exploring",
                "status_label": "Em Exploração"
            }
        
        # Calculate mastery
        correct = sum(1 for i in window if i.get("is_correct"))
        mastery = correct / actual_count
        score_pct = round(mastery * 100)
        
        # State: Building (5-6 attempts)
        if actual_count < CONFIDENCE_WINDOW:
            status_key, status_label = _get_building_status(mastery)
            return {
                "score": mastery,
                "confidence_level": "building",
                "attempts_count": actual_count,
                "attempts_needed": CONFIDENCE_WINDOW - actual_count,
                "display_value": f"{score_pct}%",
                "status_key": status_key,
                "status_label": status_label
            }
        
        # State: Established (7+ attempts)
        status_key, status_label = _get_established_status(mastery)
        return {
            "score": mastery,
            "confidence_level": "established",
            "attempts_count": actual_count,
            "attempts_needed": 0,
            "display_value": f"{score_pct}%",
            "status_key": status_key,
            "status_label": status_label
        }

    @staticmethod
    def build_results(
        concept_pairs: Iterable[tuple[str, str]],
        analytics_items: Iterable[dict]
    ) -> list[dict]:
        """
        Build per-concept results with score_data per quiz type.
        """
        # 1. Initialize Skeleton (Group by Concept)
        concept_groups: dict[tuple[str, str], list[dict]] = {}
        concept_lookup: dict[str, tuple[str, str]] = {}

        for topic_name, concept_name in concept_pairs:
            key = (topic_name, concept_name)
            concept_groups[key] = []
            norm = concept_name.strip().lower()
            if norm and norm not in concept_lookup:
                concept_lookup[norm] = key

        # 2. Group Analytics Items
        for item in analytics_items:
            t_name = item.get("topic_name")
            c_name = item.get("concept_name")
            raw_concept = item.get("raw_concept")

            key = None

            # Try direct match
            if t_name and c_name:
                key = (t_name, c_name)
            
            # Try fallback lookup
            if not key and raw_concept:
                match = concept_lookup.get(raw_concept.strip().lower())
                if match:
                    key = match
                else:
                    # Orphan concept
                    key = ("Outros", raw_concept)

            if key:
                if key not in concept_groups:
                    concept_groups[key] = []
                concept_groups[key].append(item)

        results = []

        # 3. Process Each Group
        def _created_at_key(item: dict) -> float:
            value = item.get("created_at")
            if isinstance(value, datetime):
                return value.timestamp()
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value).timestamp()
                except ValueError:
                    return 0.0
            return 0.0

        for (t_name, c_name), items in concept_groups.items():
            # Sort by created_at descending (newest first)
            sorted_items = sorted(
                items,
                key=_created_at_key,
                reverse=True
            )

            # Filter by quiz type (preserves sort order)
            mcq_items = [i for i in sorted_items if i.get("quiz_type") == "multiple-choice"]
            short_items = [i for i in sorted_items if i.get("quiz_type") == "short_answer"]
            bloom_items = [i for i in sorted_items if i.get("quiz_type") == "open-ended"]

            # Calculate score_data for each type
            score_data_mcq = AnalyticsCalculator._calculate_score_data(mcq_items)
            score_data_short = AnalyticsCalculator._calculate_score_data(short_items, EXPLORING_THRESHOLD_SHORT)
            score_data_bloom = AnalyticsCalculator._calculate_score_data(bloom_items, EXPLORING_THRESHOLD_BLOOM)

            results.append({
                "topic": t_name,
                "concept": c_name,
                # Score data per type
                "score_data_mcq": score_data_mcq,
                "score_data_short": score_data_short,
                "score_data_bloom": score_data_bloom,
                # Counts for convenience
                "total_questions_mcq": len(mcq_items),
                "total_questions_short": len(short_items),
                "total_questions_bloom": len(bloom_items),
                "total_questions": len(sorted_items),
            })

        return sorted(results, key=lambda x: (x["topic"], x["concept"]))
