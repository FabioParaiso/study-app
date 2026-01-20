from repositories.quiz_repository import QuizRepository

class AnalyticsService:
    def __init__(self, repo: QuizRepository):
        self.repo = repo

    def save_quiz_result(self, student_id: int, score: int, total: int, quiz_type: str, detailed_results: list[dict], material_id: int = None):
        return self.repo.save_quiz_result(student_id, score, total, quiz_type, detailed_results, material_id)

    def get_weak_points(self, student_id: int, material_id: int = None):
        return self.repo.get_student_analytics(student_id, material_id)

    def get_adaptive_topics(self, student_id: int, material_id: int = None):
        analytics = self.repo.get_student_analytics(student_id, material_id)
        if not analytics:
            return {"boost": [], "mastered": []}

        boost = [item["topic"] for item in analytics if item["success_rate"] < 70]
        mastered = [item["topic"] for item in analytics if item["success_rate"] >= 90]
        
        return {"boost": boost, "mastered": mastered}
