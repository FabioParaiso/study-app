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
from modules.quizzes.errors import QuizServiceError
from typing import Any


class GenerateQuizUseCase:
    def __init__(
        self,
        material_repo: MaterialLoaderPort,
        topic_selector: TopicSelectorPort,
        strategy_factory: QuizStrategyFactoryPort,
        analytics_service: Any = None # TODO: Port types
    ):
        self.material_repo = material_repo
        self.topic_selector = topic_selector
        self.strategy_factory = strategy_factory
        self.analytics_service = analytics_service

    def execute(self, user_id: int, request: QuizRequest, ai_service: QuizGeneratorPort) -> list[dict]:
        material = self.material_repo.load(user_id)
        if not material or not material.text:
            raise QuizServiceError("No material found. Upload a file first.")

        if not ai_service or not ai_service.is_available():
            raise QuizServiceError("API Key is required for quiz generation.")

        text = material.text
        material_id = material.id

        target_topics, priority_topics = self.topic_selector.select(user_id, material_id, request.topics)
        material_topics_data = MaterialMapper.topics_map(material)
        allowed_concepts = ConceptWhitelistBuilder.build(material_topics_data, target_topics)
        allowed_concepts_set = set(allowed_concepts)
        
        material_xp = material.total_xp
        try:
            strategy = self.strategy_factory.select_strategy(request.quiz_type, material_xp)
        except QuizPolicyError as e:
            raise QuizServiceError(str(e), status_code=e.status_code)

        quiz_type = request.quiz_type or "multiple-choice"
        is_multiple_choice = quiz_type == "multiple-choice"

        material_concepts: list[str] = allowed_concepts
        if is_multiple_choice:
            if self.analytics_service:
                concept_sequence = self.analytics_service.build_mcq_quiz_concepts(
                    user_id,
                    material_id,
                    allowed_concepts_set,
                    total_questions=10
                )
            else:
                concept_sequence = []

            if not concept_sequence and allowed_concepts:
                idx = 0
                while len(concept_sequence) < 10:
                    concept_sequence.append(allowed_concepts[idx % len(allowed_concepts)])
                    idx += 1

            material_concepts = concept_sequence

        questions = ai_service.generate_quiz(strategy, text, target_topics, priority_topics, material_concepts)
        
        if not questions:
            raise QuizServiceError("Failed to generate quiz. Please try again.", status_code=500)

        post_processor = QuestionPostProcessor(request.quiz_type)
        return post_processor.apply(questions)


class EvaluateAnswerUseCase:
    def __init__(
        self,
        material_repo: MaterialLoaderPort,
        strategy_factory: QuizStrategyFactoryPort
    ):
        self.material_repo = material_repo
        self.strategy_factory = strategy_factory

    def execute(self, user_id: int, request: EvaluationRequest, ai_service: AnswerEvaluatorPort) -> dict:
        material = self.material_repo.load(user_id)
        if not material or not material.text:
            raise QuizServiceError("No material found.")

        if not ai_service or not ai_service.is_available():
            raise QuizServiceError("API Key is required for evaluation.")

        text = material.text
        strategy = self.strategy_factory.select_evaluation_strategy(request.quiz_type)
        return ai_service.evaluate_answer(strategy, text, request.question, request.user_answer)


class SaveQuizResultUseCase:
    def __init__(
        self,
        material_repo: MaterialLoaderPort,
        recorder: QuizResultRecorderPort
    ):
        self.material_repo = material_repo
        self.recorder = recorder

    def execute(self, user_id: int, result: QuizResultCreate) -> None:
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
