from fastapi import Depends
from sqlalchemy.orm import Session
import os
from database import get_db
from modules.analytics.repository import AnalyticsRepository
from modules.analytics.service import AnalyticsService
from modules.materials.repository import (
    MaterialConceptRepository,
    MaterialReadRepository,
    MaterialStatsRepository,
)
from modules.quizzes.ai_service import QuizAIService
from modules.materials.stats import MaterialStatsUpdater
from modules.quizzes.concept_resolver import ConceptIdResolver
from modules.quizzes.policies import AdaptiveTopicSelector, QuizStrategyFactory
from modules.quizzes.recorder import QuizResultRecorder
from modules.quizzes.repository import QuizResultWriterRepository
from modules.quizzes.service import QuizService
from modules.quizzes.ports import QuizResultWriterPort


def get_material_read_repo(db: Session = Depends(get_db)):
    return MaterialReadRepository(db)


def get_material_concept_repo(db: Session = Depends(get_db)):
    return MaterialConceptRepository(db)


def get_material_stats_repo(db: Session = Depends(get_db)):
    return MaterialStatsRepository(db)


def get_quiz_repo(db: Session = Depends(get_db)):
    return QuizResultWriterRepository(db)


def get_analytics_repo(db: Session = Depends(get_db)):
    return AnalyticsRepository(db)


def get_ai_service(api_key: str | None = None):
    key = api_key or os.getenv("OPENAI_API_KEY")
    return QuizAIService(key)


def get_quiz_service(
    material_repo: MaterialReadRepository = Depends(get_material_read_repo),
    concept_repo: MaterialConceptRepository = Depends(get_material_concept_repo),
    stats_repo: MaterialStatsRepository = Depends(get_material_stats_repo),
    quiz_repo: QuizResultWriterPort = Depends(get_quiz_repo),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repo)
):
    analytics_service = AnalyticsService(analytics_repo, concept_repo)
    topic_selector = AdaptiveTopicSelector(analytics_service)
    strategy_factory = QuizStrategyFactory()
    resolver = ConceptIdResolver(concept_repo)
    stats_updater = MaterialStatsUpdater(stats_repo)
    recorder = QuizResultRecorder(quiz_repo, resolver, stats_updater)
    return QuizService(
        material_repo,
        topic_selector=topic_selector,
        strategy_factory=strategy_factory,
        recorder=recorder
    )
