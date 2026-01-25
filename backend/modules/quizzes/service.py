from schemas.study import QuizRequest, EvaluationRequest, QuizResultCreate
from modules.analytics.service import AnalyticsService
from modules.materials.stats import MaterialStatsUpdater
from modules.quizzes.concept_resolver import ConceptIdResolver
from modules.quizzes.policies import (
    AdaptiveTopicSelector,
    ConceptWhitelistBuilder,
    QuestionPostProcessor,
    QuizPolicyError,
    QuizUnlockPolicy,
)
from services.ports import AnalyticsRepositoryPort, MaterialRepositoryPort, QuizRepositoryPort, QuizAIServicePort


class QuizServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class QuizService:
    def __init__(self, material_repo: MaterialRepositoryPort, quiz_repo: QuizRepositoryPort, analytics_repo: AnalyticsRepositoryPort):
        self.material_repo = material_repo
        self.quiz_repo = quiz_repo
        self.analytics_repo = analytics_repo

    def generate_quiz(self, user_id: int, request: QuizRequest, ai_service: QuizAIServicePort) -> list[dict]:
        data = self.material_repo.load(user_id)
        if not data or not data.get("text"):
            raise QuizServiceError("No material found. Upload a file first.")

        if not ai_service or not ai_service.client:
            raise QuizServiceError("API Key is required for quiz generation.")

        text = data.get("text")

        analytics_service = AnalyticsService(self.analytics_repo, self.material_repo)
        material_id = data.get("id")

        selector = AdaptiveTopicSelector(analytics_service)
        target_topics, priority_topics = selector.select(user_id, material_id, request.topics)

        material_xp = data.get("total_xp", 0)
        unlock_policy = QuizUnlockPolicy(material_xp)
        try:
            strategy = unlock_policy.select_strategy(request.quiz_type)
        except QuizPolicyError as e:
            raise QuizServiceError(str(e), status_code=e.status_code)

        material_topics_data = data.get("topics", {})
        material_concepts = ConceptWhitelistBuilder.build(material_topics_data, target_topics)

        questions = ai_service.generate_quiz(strategy, text, target_topics, priority_topics, material_concepts)
        if not questions:
            raise QuizServiceError("Failed to generate quiz. Please try again.", status_code=500)

        post_processor = QuestionPostProcessor(request.quiz_type)
        return post_processor.apply(questions)

    def evaluate_answer(self, user_id: int, request: EvaluationRequest, ai_service: QuizAIServicePort) -> dict:
        data = self.material_repo.load(user_id)
        if not data or not data.get("text"):
            raise QuizServiceError("No material found.")

        if not ai_service or not ai_service.client:
            raise QuizServiceError("API Key is required for evaluation.")

        text = data.get("text")
        return ai_service.evaluate_answer(text, request.question, request.user_answer, request.quiz_type)

    def save_quiz_result(self, user_id: int, result: QuizResultCreate) -> None:
        material_id = result.study_material_id
        if not material_id:
            current = self.material_repo.load(user_id)
            material_id = current["id"] if current else None

        analytics_data = [item.dict() for item in result.detailed_results]
        resolver = ConceptIdResolver(self.material_repo)
        analytics_data = resolver.apply(material_id, analytics_data)
        success = self.quiz_repo.save_quiz_result(
            student_id=user_id,
            score=result.score,
            total=result.total_questions,
            quiz_type=result.quiz_type,
            analytics_data=analytics_data,
            material_id=material_id
        )
        if not success:
            raise QuizServiceError("Failed to save results", status_code=500)

        if material_id:
            updater = MaterialStatsUpdater(self.material_repo)
            updated = updater.apply(
                material_id=material_id,
                score=result.score,
                total_questions=result.total_questions,
                xp_earned=result.xp_earned
            )
            if not updated:
                raise QuizServiceError("Failed to update material stats", status_code=500)

    def get_weak_points(self, user_id: int, material_id: int | None = None) -> list[dict]:
        if not material_id:
            current = self.material_repo.load(user_id)
            if not current:
                return []
            material_id = current["id"]

        analytics = AnalyticsService(self.analytics_repo, self.material_repo)
        return analytics.get_weak_points(user_id, material_id)
