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
