from schemas.study import QuizRequest, EvaluationRequest, QuizResultCreate
from typing import Any
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

    @staticmethod
    def _build_concept_sequence(analytics_service, user_id, material_id, allowed_set, allowed_list, builder, total):
        sequence = []
        if analytics_service:
            sequence = getattr(analytics_service, builder)(user_id, material_id, allowed_set, total_questions=total)
        if not sequence and allowed_list:
            sequence = [allowed_list[i % len(allowed_list)] for i in range(total)]
        return sequence

    @staticmethod
    def _questions_have_concepts(questions: list[dict] | None) -> bool:
        if not isinstance(questions, list) or not questions:
            return False
        for question in questions:
            if not isinstance(question, dict):
                return False
            concepts = question.get("concepts")
            if not isinstance(concepts, list):
                return False
            if not any(isinstance(c, str) and c.strip() for c in concepts):
                return False
        return True

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

        material_xp = material.total_xp
        try:
            strategy = self.strategy_factory.select_strategy(request.quiz_type, material_xp)
        except QuizPolicyError as e:
            raise QuizServiceError(str(e), status_code=e.status_code)

        quiz_type = request.quiz_type or "multiple-choice"
        is_multiple_choice = quiz_type == "multiple-choice"
        is_short_answer = quiz_type == "short_answer"

        # Gate: short answer requires all concepts to have confident MCQ data
        if is_short_answer and self.analytics_service:
            readiness = self.analytics_service.check_short_answer_readiness(user_id, material_id)
            if not readiness["is_ready"]:
                ready = readiness["ready_concepts"]
                total = readiness["total_concepts"]
                raise QuizServiceError(
                    f"Ainda não estás pronto para o Intermédio. "
                    f"Pratica mais no Quiz Rápido ({ready}/{total} conceitos prontos).",
                    status_code=403
                )

        material_concepts: list[str] = allowed_concepts
        if is_multiple_choice or is_short_answer:
            # For fixed-sequence quizzes, only restrict concepts by the user's
            # explicit topic selection — not by adaptive topic filtering.
            # The concept builders already handle internal prioritisation.
            quiz_concepts = ConceptWhitelistBuilder.build(material_topics_data, request.topics)
            quiz_concepts_set = set(quiz_concepts)

            if is_multiple_choice:
                material_concepts = self._build_concept_sequence(
                    self.analytics_service, user_id, material_id, quiz_concepts_set, quiz_concepts,
                    builder="build_mcq_quiz_concepts", total=10
                )
            else:
                material_concepts = self._build_concept_sequence(
                    self.analytics_service, user_id, material_id, quiz_concepts_set, quiz_concepts,
                    builder="build_short_quiz_concepts", total=8
                )

        questions = ai_service.generate_quiz(strategy, text, target_topics, priority_topics, material_concepts)

        if not self._questions_have_concepts(questions):
            questions = ai_service.generate_quiz(strategy, text, target_topics, priority_topics, material_concepts)

        if not self._questions_have_concepts(questions):
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

        analytics_data = [
            item.model_dump() if hasattr(item, "model_dump") else item.dict()
            for item in result.detailed_results
        ]
        if not analytics_data:
            raise QuizServiceError("Resultados detalhados em falta.", status_code=400)
        try:
            self.recorder.record(
                user_id=user_id,
                score=result.score,
                total_questions=result.total_questions,
                quiz_type=result.quiz_type,
                analytics_data=analytics_data,
                material_id=material_id,
                xp_earned=result.xp_earned,
                duration_seconds=result.duration_seconds,
                active_seconds=result.active_seconds
            )
        except QuizRecordError as e:
            raise QuizServiceError(str(e), status_code=e.status_code)
