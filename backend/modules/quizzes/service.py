from schemas.study import QuizRequest, EvaluationRequest, QuizResultCreate
from modules.materials.mapper import MaterialMapper
from modules.quizzes.recorder import QuizRecordError
from modules.quizzes.policies import (
    ConceptWhitelistBuilder,
    QuestionPostProcessor,
    QuizPolicyError,
)
from modules.materials.ports import MaterialLoaderPort, TopicSelectorPort
from modules.quizzes.ports import (
    QuizGeneratorPort,
    AnswerEvaluatorPort,
    QuizResultRecorderPort,
    QuizStrategyFactoryPort,
)


class QuizServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class QuizService:
    def __init__(
        self,
        material_repo: MaterialLoaderPort,
        topic_selector: TopicSelectorPort,
        strategy_factory: QuizStrategyFactoryPort,
        recorder: QuizResultRecorderPort
    ):
        self.material_repo = material_repo
        self.topic_selector = topic_selector
        self.strategy_factory = strategy_factory
        self.recorder = recorder

    def generate_quiz(self, user_id: int, request: QuizRequest, ai_service: QuizGeneratorPort) -> list[dict]:
        material = self.material_repo.load(user_id)
        if not material or not material.text:
            raise QuizServiceError("No material found. Upload a file first.")

        if not ai_service or not ai_service.client:
            raise QuizServiceError("API Key is required for quiz generation.")

        text = material.text

        material_id = material.id

        target_topics, priority_topics = self.topic_selector.select(user_id, material_id, request.topics)

        material_xp = material.total_xp
        try:
            strategy = self.strategy_factory.select_strategy(request.quiz_type, material_xp)
        except QuizPolicyError as e:
            raise QuizServiceError(str(e), status_code=e.status_code)

        material_topics_data = MaterialMapper.topics_map(material)
        material_concepts = ConceptWhitelistBuilder.build(material_topics_data, target_topics)

        questions = ai_service.generate_quiz(strategy, text, target_topics, priority_topics, material_concepts)
        if not questions:
            raise QuizServiceError("Failed to generate quiz. Please try again.", status_code=500)

        post_processor = QuestionPostProcessor(request.quiz_type)
        return post_processor.apply(questions)

    def evaluate_answer(self, user_id: int, request: EvaluationRequest, ai_service: AnswerEvaluatorPort) -> dict:
        material = self.material_repo.load(user_id)
        if not material or not material.text:
            raise QuizServiceError("No material found.")

        if not ai_service or not ai_service.client:
            raise QuizServiceError("API Key is required for evaluation.")

        text = material.text

        # Using factory to select evaluation strategy
        strategy = self.strategy_factory.select_evaluation_strategy(request.quiz_type)

        return ai_service.evaluate_answer(strategy, text, request.question, request.user_answer)

    def save_quiz_result(self, user_id: int, result: QuizResultCreate) -> None:
        material_id = result.study_material_id
        if not material_id:
            current = self.material_repo.load(user_id)
            material_id = current.id if current else None

        analytics_data = [item.dict() for item in result.detailed_results]
        try:
            self.recorder.record(
                user_id=user_id,
                score=result.score,
                total_questions=result.total_questions,
                quiz_type=result.quiz_type,
                analytics_data=analytics_data,
                material_id=material_id,
                xp_earned=result.xp_earned
            )
        except QuizRecordError as e:
            raise QuizServiceError(str(e), status_code=e.status_code)
