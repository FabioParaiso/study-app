from fastapi import Depends
from sqlalchemy.orm import Session
import os
from database import get_db
from modules.analytics.repository import AnalyticsRepository
from modules.materials.repository import MaterialRepository
from modules.quizzes.ai_service import QuizAIService
from modules.quizzes.repository import QuizRepository
from modules.quizzes.service import QuizService


def get_material_repo(db: Session = Depends(get_db)):
    return MaterialRepository(db)


def get_quiz_repo(db: Session = Depends(get_db)):
    return QuizRepository(db)


def get_analytics_repo(db: Session = Depends(get_db)):
    return AnalyticsRepository(db)


def get_ai_service(api_key: str | None = None):
    key = api_key or os.getenv("OPENAI_API_KEY")
    return QuizAIService(key)


def get_quiz_service(
    material_repo: MaterialRepository = Depends(get_material_repo),
    quiz_repo: QuizRepository = Depends(get_quiz_repo),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repo)
):
    return QuizService(material_repo, quiz_repo, analytics_repo)
