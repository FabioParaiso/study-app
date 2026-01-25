from typing import Iterable
from datetime import datetime


class AnalyticsCalculator:
    @staticmethod
    def build_results(
        concept_pairs: Iterable[tuple[str, str]],
        analytics_items: Iterable[dict]
    ) -> list[dict]:
        """
        Build per-concept success rates using Effective Mastery logic.
        Effective = Mastery (last 10) * Confidence + 0.5 * (1 - Confidence)
        """
        # 1. Initialize Skeleton (Group by Concept)
        # key = (topic_name, concept_name) normalized
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
            # Handle potential None created_at (though schema should enforce it, be safe)
            sorted_items = sorted(
                items,
                key=_created_at_key,
                reverse=True
            )

            # Slice Window
            window = sorted_items[:WINDOW_SIZE]
            count = len(window)

            if count == 0:
                results.append({
                    "topic": t_name,
                    "concept": c_name,
                    "success_rate": 0,
                    "total_questions": 0,
                    "mastery_raw": 0,
                    "status": "Não visto"
                })
                continue

            # Calculate Metrics
            correct_count = sum(1 for i in window if i.get("is_correct"))
            mastery = correct_count / count
            
            confidence = min(1.0, count / float(WINDOW_SIZE))
            
            effective_score = (mastery * confidence) + (0.5 * (1 - confidence))
            
            # Map to Percentage (0-100)
            final_percentage = round(effective_score * 100)

            # Determine Status
            status = "Em aprendizagem"
            if count >= 3: # Reasonable threshold to start giving labels
                 if effective_score >= 0.8:
                     status = "Forte"
                 elif effective_score >= 0.65:
                     status = "Ok"
                 else:
                     status = "Fraco"
            elif count > 0:
                status = "Em aprendizagem"

            results.append({
                "topic": t_name,
                "concept": c_name,
                "success_rate": final_percentage,
                "total_questions": len(items), # Total history count
                "mastery_raw": round(mastery * 100),
                "status": status
            })

        return sorted(results, key=lambda x: (x["topic"], x["success_rate"]))
