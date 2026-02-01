import random
from modules.analytics.calculator import AnalyticsCalculator
from modules.analytics.ports import AnalyticsRepositoryPort
from modules.materials.ports import MaterialConceptPairsRepositoryPort

class AnalyticsService:
    def __init__(self, analytics_repo: AnalyticsRepositoryPort, material_repo: MaterialConceptPairsRepositoryPort):
        self.analytics_repo = analytics_repo
        self.material_repo = material_repo

    def get_weak_points(self, student_id: int, material_id: int = None):
        if material_id:
            concept_pairs = self.material_repo.get_concept_pairs(material_id)
        else:
            concept_pairs = self.material_repo.get_concept_pairs_for_student(student_id)

        analytics_items = self.analytics_repo.fetch_question_analytics(student_id, material_id)
        
        # DEBUG PRINTS
        print(f"DEBUG: get_weak_points material_id={material_id}")
        print(f"DEBUG: concept_pairs={concept_pairs}")
        print(f"DEBUG: analytics_items count={len(analytics_items)}")
        
        return AnalyticsCalculator.build_results(concept_pairs, analytics_items)

    def get_adaptive_topics(self, student_id: int, material_id: int = None):
        analytics = self.get_weak_points(student_id, material_id)
        if not analytics:
            return {"boost": [], "mastered": []}

        def _unique_topics(items: list[str]) -> list[str]:
            seen: set[str] = set()
            unique: list[str] = []
            for topic in items:
                if topic not in seen:
                    seen.add(topic)
                    unique.append(topic)
            return unique

        boost = _unique_topics([item["topic"] for item in analytics if item["success_rate"] < 70])
        mastered = _unique_topics([item["topic"] for item in analytics if item["success_rate"] >= 90])
        
        return {"boost": boost, "mastered": mastered}

    def get_classified_concepts(self, student_id: int, material_id: int | None = None) -> dict[str, list[str]]:
        results = self.get_weak_points(student_id, material_id)
        
        unseen = []
        weak = []
        strong = []
        
        for item in results:
            concept = item["concept"]
            if not concept:
                continue

            mcq_count = item.get("total_questions_mcq", 0)
            effective_mcq = item.get("effective_mcq", 0)

            if mcq_count == 0:
                unseen.append(concept)
            elif effective_mcq <= 75:
                # <= 75% includes "Weak" and "Learning" (Fraco/Em aprendizagem) for MCQ only
                weak.append(concept)
            else:
                # > 75% includes "Strong" (Forte/Ok) for MCQ only
                strong.append(concept)
                
        return {
            "unseen": unseen,
            "weak": weak,
            "strong": strong
        }

    def build_mcq_quiz_concepts(
        self,
        student_id: int,
        material_id: int | None = None,
        allowed_concepts: set[str] | None = None,
        total_questions: int = 10
    ) -> list[str]:
        results = self.get_weak_points(student_id, material_id)

        items: list[dict] = []
        for item in results:
            concept = item.get("concept")
            if not concept:
                continue
            if allowed_concepts and concept not in allowed_concepts:
                continue
            items.append({
                "concept": concept,
                "effective_mcq": item.get("effective_mcq", 0),
                "total_questions_mcq": item.get("total_questions_mcq", 0),
            })

        if not items or total_questions <= 0:
            return []

        unseen_items = [i for i in items if i["total_questions_mcq"] == 0]
        weak_items = [i for i in items if i["total_questions_mcq"] > 0 and i["effective_mcq"] <= 75]
        strong_items = [i for i in items if i["total_questions_mcq"] > 0 and i["effective_mcq"] > 75]

        unseen_items = sorted(unseen_items, key=lambda i: i["concept"].lower())
        weak_items = sorted(weak_items, key=lambda i: (i["effective_mcq"], i["concept"].lower()))
        strong_items = sorted(strong_items, key=lambda i: (i["effective_mcq"], i["concept"].lower()))

        def _repeat_by_weight(
            bucket: list[dict],
            count: int,
            weight_fn=None,
            ensure_each_once: bool = True
        ) -> list[str]:
            if count <= 0 or not bucket:
                return []

            concepts = [i["concept"] for i in bucket]
            if ensure_each_once and count <= len(concepts):
                return concepts[:count]

            selected: list[str] = []
            remaining = count
            if ensure_each_once:
                selected = concepts[:]
                remaining = count - len(concepts)

            if remaining <= 0:
                return selected

            if weight_fn is None:
                idx = 0
                while remaining > 0:
                    selected.append(concepts[idx % len(concepts)])
                    idx += 1
                    remaining -= 1
                return selected

            weights = [max(1, int(weight_fn(i))) for i in bucket]
            total_weight = sum(weights)
            allocations = [int((w / total_weight) * remaining) for w in weights]
            allocated = sum(allocations)
            remainder = remaining - allocated
            order = sorted(
                range(len(bucket)),
                key=lambda i: (-weights[i], concepts[i].lower())
            )
            for i in range(remainder):
                allocations[order[i % len(order)]] += 1
            for idx, count in enumerate(allocations):
                if count > 0:
                    selected.extend([concepts[idx]] * count)
            return selected

        def _fill(bucket: list[dict], count: int, weight_fn=None) -> tuple[list[str], int]:
            if count <= 0:
                return [], 0
            if not bucket:
                return [], count
            return _repeat_by_weight(bucket, count, weight_fn=weight_fn, ensure_each_once=True), 0

        def _weak_weight(item: dict) -> int:
            return max(1, 100 - int(item.get("effective_mcq", 0)))

        selected: list[str] = []
        shortage = 0

        unseen_selected, shortage = _fill(unseen_items, 5)
        selected.extend(unseen_selected)

        weak_selected, shortage = _fill(weak_items, 4 + shortage, weight_fn=_weak_weight)
        selected.extend(weak_selected)

        strong_selected, shortage = _fill(strong_items, 1 + shortage)
        selected.extend(strong_selected)

        if shortage > 0:
            fallback_bucket = weak_items or unseen_items or strong_items
            if fallback_bucket:
                fallback_weight = _weak_weight if fallback_bucket is weak_items else None
                selected.extend(
                    _repeat_by_weight(
                        fallback_bucket,
                        shortage,
                        weight_fn=fallback_weight,
                        ensure_each_once=False
                    )
                )

        selected = selected[:total_questions]
        random.shuffle(selected)
        return selected
