from fastapi import APIRouter, Depends, HTTPException
from modules.quizzes.deps import get_ai_service, get_quiz_service
from modules.quizzes.service import QuizService, QuizServiceError
from schemas.study import QuizRequest, EvaluationRequest, QuizResultCreate
from dependencies import get_current_user
from models import Student

router = APIRouter()

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
