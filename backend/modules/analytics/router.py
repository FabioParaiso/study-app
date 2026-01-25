from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from modules.materials.repository import MaterialRepository
from modules.analytics.repository import AnalyticsRepository
from modules.quizzes.repository import QuizRepository
from modules.quizzes.service import QuizService
from dependencies import get_current_user
from models import Student

router = APIRouter()

# --- Dependencies ---
def get_material_repo(db: Session = Depends(get_db)):
    return MaterialRepository(db)

def get_quiz_repo(db: Session = Depends(get_db)):
    return QuizRepository(db)

def get_analytics_repo(db: Session = Depends(get_db)):
    return AnalyticsRepository(db)

def get_quiz_service(
    material_repo: MaterialRepository = Depends(get_material_repo),
    quiz_repo: QuizRepository = Depends(get_quiz_repo),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repo)
):
    return QuizService(material_repo, quiz_repo, analytics_repo)

# --- Endpoints ---
@router.get("/analytics/weak-points")
def get_weak_points(
    current_user: Student = Depends(get_current_user),
    material_id: int | None = None,
    quiz_service: QuizService = Depends(get_quiz_service)
):
    return quiz_service.get_weak_points(current_user.id, material_id)
