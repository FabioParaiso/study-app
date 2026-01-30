from fastapi import Depends
from sqlalchemy.orm import Session
import os
from database import get_db
from modules.analytics.repository import AnalyticsRepository
from modules.analytics.service import AnalyticsService
from modules.materials.repository import (
    MaterialConceptRepository,
    MaterialReadRepository,
)
from modules.quizzes.ai_service import QuizAIService
from modules.quizzes.concept_resolver import ConceptIdResolver
from modules.quizzes.policies import AdaptiveTopicSelector, QuizStrategyFactory
from modules.quizzes.recorder import QuizResultRecorder
from modules.quizzes.repository import QuizResultPersistenceRepository
from modules.quizzes.use_cases import (
    GenerateQuizUseCase,
    EvaluateAnswerUseCase,
    SaveQuizResultUseCase,
)
from modules.quizzes.registry import build_default_quiz_registry
from modules.quizzes.ports import QuizResultPersistencePort
from services.llm_provider import build_openai_caller


def get_material_read_repo(db: Session = Depends(get_db)):
    return MaterialReadRepository(db)


def get_material_concept_repo(db: Session = Depends(get_db)):
    return MaterialConceptRepository(db)


def get_quiz_repo(db: Session = Depends(get_db)):
    return QuizResultPersistenceRepository(db)


def get_analytics_repo(db: Session = Depends(get_db)):
    return AnalyticsRepository(db)


def get_ai_service(api_key: str | None = None):
    key = api_key or os.getenv("OPENAI_API_KEY")
    caller = build_openai_caller(key)
    return QuizAIService(caller)

def get_generate_quiz_use_case(
    material_repo: MaterialReadRepository = Depends(get_material_read_repo),
    concept_repo: MaterialConceptRepository = Depends(get_material_concept_repo),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repo)
):
    analytics_service = AnalyticsService(analytics_repo, concept_repo)
    topic_selector = AdaptiveTopicSelector(analytics_service)
    strategy_factory = QuizStrategyFactory(build_default_quiz_registry())
    return GenerateQuizUseCase(material_repo, topic_selector, strategy_factory, analytics_service)


def get_evaluate_answer_use_case(
    material_repo: MaterialReadRepository = Depends(get_material_read_repo),
):
    strategy_factory = QuizStrategyFactory(build_default_quiz_registry())
    return EvaluateAnswerUseCase(material_repo, strategy_factory)


def get_save_quiz_result_use_case(
    material_repo: MaterialReadRepository = Depends(get_material_read_repo),
    concept_repo: MaterialConceptRepository = Depends(get_material_concept_repo),
    quiz_repo: QuizResultPersistencePort = Depends(get_quiz_repo),
):
    resolver = ConceptIdResolver(concept_repo)
    recorder = QuizResultRecorder(quiz_repo, resolver)
    return SaveQuizResultUseCase(material_repo, recorder)
