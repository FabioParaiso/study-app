from typing import Iterable
from datetime import datetime


class AnalyticsCalculator:
    @staticmethod
    def _calculate_effective_score(items: list[dict], window_size: int = 10) -> float:
        if not items:
            return 0.0
        
        # Items are expected to be sorted by recency (newest first)
        window = items[:window_size]
        count = len(window)
        
        correct_count = sum(1 for i in window if i.get("is_correct"))
        mastery = correct_count / count
        
        confidence = min(1.0, count / float(window_size))
        
        return (mastery * confidence) + (0.5 * (1 - confidence))

    @staticmethod
    def build_results(
        concept_pairs: Iterable[tuple[str, str]],
        analytics_items: Iterable[dict]
    ) -> list[dict]:
        """
        Build per-concept success rates using Effective Mastery logic.
        Effective = Mastery (last 10) * Confidence + 0.5 * (1 - Confidence)
        Now split by mode: MCQ, Short, Bloom.
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
        WINDOW_SIZE = 10

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

            # --- Overall Metric (Legacy Support) ---
            # We still calculate this for backward compatibility and general overview
            effective_overall = AnalyticsCalculator._calculate_effective_score(sorted_items, WINDOW_SIZE)
            
            # Raw Mastery for display (all time? or window? stored logic used window)
            # Replicating original logic for mastery_raw:
            window = sorted_items[:WINDOW_SIZE]
            if window:
                mastery_raw = sum(1 for i in window if i.get("is_correct")) / len(window)
            else:
                mastery_raw = 0.0

            # --- Split Metrics ---
            # Filter preserves the sort order (recency)
            mcq_items = [i for i in sorted_items if i.get("quiz_type") == "multiple-choice"]
            short_items = [i for i in sorted_items if i.get("quiz_type") == "short_answer"]
            bloom_items = [i for i in sorted_items if i.get("quiz_type") == "open-ended"]

            effective_mcq = AnalyticsCalculator._calculate_effective_score(mcq_items, WINDOW_SIZE)
            effective_short = AnalyticsCalculator._calculate_effective_score(short_items, WINDOW_SIZE)
            effective_bloom = AnalyticsCalculator._calculate_effective_score(bloom_items, WINDOW_SIZE)

            count_mcq = len(mcq_items)
            count_short = len(short_items)
            count_bloom = len(bloom_items)

            # Map to Percentage (0-100)
            final_percentage = round(effective_overall * 100)

            # Determine Status (based on Overall for now, or maybe highest?)
            # Keeping original logic based on overall effective score
            status = "Em aprendizagem"
            count = len(sorted_items)
            
            if count >= 3:
                 if effective_overall >= 0.8:
                     status = "Forte"
                 elif effective_overall >= 0.65:
                     status = "Ok"
                 else:
                     status = "Fraco"
            elif count > 0:
                status = "Em aprendizagem"
            else:
                status = "Não visto"

            results.append({
                "topic": t_name,
                "concept": c_name,
                "success_rate": final_percentage,
                "effective_mcq": round(effective_mcq * 100),
                "effective_short": round(effective_short * 100),
                "effective_bloom": round(effective_bloom * 100),
                "total_questions_mcq": count_mcq,
                "total_questions_short": count_short,
                "total_questions_bloom": count_bloom,
                "total_questions": count,
                "mastery_raw": round(mastery_raw * 100),
                "status": status
            })

        return sorted(results, key=lambda x: (x["topic"], x["success_rate"]))
