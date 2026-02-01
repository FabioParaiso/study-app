from modules.quizzes.concept_resolver import ConceptIdResolver
from modules.quizzes.ports import QuizResultPersistencePort


class QuizRecordError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


class QuizResultRecorder:
    def __init__(
        self,
        quiz_repo: QuizResultPersistencePort,
        resolver: ConceptIdResolver
    ):
        self.quiz_repo = quiz_repo
        self.resolver = resolver

    def record(
        self,
        user_id: int,
        score: int,
        total_questions: int,
        quiz_type: str,
        analytics_data: list[dict],
        material_id: int | None,
        xp_earned: int,
        duration_seconds: int,
        active_seconds: int
    ) -> None:
        analytics_data = self.resolver.apply(material_id, analytics_data)
        success = self.quiz_repo.record_quiz_result(
            student_id=user_id,
            score=score,
            total=total_questions,
            quiz_type=quiz_type,
            analytics_data=analytics_data,
            material_id=material_id,
            xp_earned=xp_earned,
            duration_seconds=duration_seconds,
            active_seconds=active_seconds
        )
        if not success:
            raise QuizRecordError("Failed to save results", status_code=500)
