from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from database import get_db
from modules.materials.repository import MaterialRepository
from modules.analytics.repository import AnalyticsRepository
from modules.quizzes.repository import QuizRepository
from modules.quizzes.service import QuizService, QuizServiceError
from schemas.study import QuizRequest, EvaluationRequest, QuizResultCreate
from dependencies import get_current_user
from models import Student
from modules.quizzes.ai_service import QuizAIService

router = APIRouter()

# --- Dependencies ---
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

# --- Endpoints ---
@router.post("/generate-quiz")
def generate_quiz_endpoint(
    request: QuizRequest,
    current_user: Student = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    ai_service = get_ai_service(request.api_key)
    try:
        questions = quiz_service.generate_quiz(current_user.id, request, ai_service)
    except QuizServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return {"questions": questions}

@router.post("/evaluate-answer")
def evaluate_answer_endpoint(
    request: EvaluationRequest,
    current_user: Student = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    ai_service = get_ai_service(request.api_key)
    try:
        return quiz_service.evaluate_answer(current_user.id, request, ai_service)
    except QuizServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.post("/quiz/result")
def save_quiz_result(
    result: QuizResultCreate,
    current_user: Student = Depends(get_current_user),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    try:
        quiz_service.save_quiz_result(current_user.id, result)
    except QuizServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return {"status": "saved"}
