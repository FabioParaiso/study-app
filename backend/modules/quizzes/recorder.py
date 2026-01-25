from modules.materials.stats import MaterialStatsUpdater
from modules.quizzes.concept_resolver import ConceptIdResolver
from modules.quizzes.ports import QuizResultWriterPort


class QuizRecordError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


class QuizResultRecorder:
    def __init__(
        self,
        quiz_repo: QuizResultWriterPort,
        resolver: ConceptIdResolver,
        stats_updater: MaterialStatsUpdater
    ):
        self.quiz_repo = quiz_repo
        self.resolver = resolver
        self.stats_updater = stats_updater

    def record(
        self,
        user_id: int,
        score: int,
        total_questions: int,
        quiz_type: str,
        analytics_data: list[dict],
        material_id: int | None,
        xp_earned: int
    ) -> None:
        analytics_data = self.resolver.apply(material_id, analytics_data)
        success = self.quiz_repo.save_quiz_result(
            student_id=user_id,
            score=score,
            total=total_questions,
            quiz_type=quiz_type,
            analytics_data=analytics_data,
            material_id=material_id
        )
        if not success:
            raise QuizRecordError("Failed to save results", status_code=500)

        if material_id:
            updated = self.stats_updater.apply(
                material_id=material_id,
                score=score,
                total_questions=total_questions,
                xp_earned=xp_earned
            )
            if not updated:
                raise QuizRecordError("Failed to update material stats", status_code=500)
