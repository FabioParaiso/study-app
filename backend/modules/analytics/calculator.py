from typing import Iterable


class AnalyticsCalculator:
    @staticmethod
    def build_results(
        concept_pairs: Iterable[tuple[str, str]],
        analytics_items: Iterable[dict]
    ) -> list[dict]:
        """
        Build per-concept success rates from a concept skeleton + analytics items.
        analytics_items expects: concept_name, topic_name, raw_concept, is_correct.
        """
        skeleton: dict[tuple[str, str], dict[str, int]] = {}
        concept_lookup: dict[str, tuple[str, str]] = {}

        for topic_name, concept_name in concept_pairs:
            key = (topic_name, concept_name)
            skeleton[key] = {"total": 0, "correct": 0}
            norm = concept_name.strip().lower()
            if norm and norm not in concept_lookup:
                concept_lookup[norm] = key

        for item in analytics_items:
            t_name = item.get("topic_name")
            c_name = item.get("concept_name")
            raw_concept = item.get("raw_concept")

            if not t_name or not c_name:
                if raw_concept:
                    match = concept_lookup.get(raw_concept.lower())
                    if match:
                        t_name, c_name = match
                    else:
                        t_name = "Outros"
                        c_name = raw_concept

            if not t_name or not c_name:
                continue

            key = (t_name, c_name)
            if key not in skeleton:
                skeleton[key] = {"total": 0, "correct": 0}

            skeleton[key]["total"] += 1
            if item.get("is_correct"):
                skeleton[key]["correct"] += 1

        results = []
        for (t_name, c_name), stats in skeleton.items():
            total = stats["total"]
            correct = stats["correct"]
            rate = round((correct / total) * 100) if total > 0 else 0
            results.append(
                {
                    "topic": t_name,
                    "concept": c_name,
                    "success_rate": rate,
                    "total_questions": total,
                }
            )

        return sorted(results, key=lambda x: (x["topic"], x["success_rate"]))
