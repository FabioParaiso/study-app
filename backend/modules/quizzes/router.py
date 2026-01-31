from fastapi import APIRouter, Depends, HTTPException, Request
import os
from modules.quizzes.deps import (
    get_ai_service,
    get_generate_quiz_use_case,
    get_evaluate_answer_use_case,
    get_save_quiz_result_use_case,
)
from modules.quizzes.errors import QuizServiceError
from schemas.study import QuizRequest, EvaluationRequest, QuizResultCreate
from dependencies import get_current_user, enforce_ai_quota
from models import Student
from modules.quizzes.ports import (
    QuizAIServicePort,
    GenerateQuizUseCasePort,
    EvaluateAnswerUseCasePort,
    SaveQuizResultUseCasePort,
)

from rate_limiter import limiter

router = APIRouter()
AI_RATE_LIMIT = os.getenv("AI_RATE_LIMIT", "20/minute")

def get_quiz_ai_service(payload: QuizRequest) -> QuizAIServicePort:
    return get_ai_service(payload.api_key)


def get_eval_ai_service(payload: EvaluationRequest) -> QuizAIServicePort:
    return get_ai_service(payload.api_key)


# --- Endpoints ---
@router.post("/generate-quiz")
@limiter.limit(AI_RATE_LIMIT)
def generate_quiz_endpoint(
    request: Request,
    payload: QuizRequest,
    current_user: Student = Depends(get_current_user),
    _quota: None = Depends(enforce_ai_quota),
    use_case: GenerateQuizUseCasePort = Depends(get_generate_quiz_use_case),
    ai_service: QuizAIServicePort = Depends(get_quiz_ai_service)
):
    try:
        questions = use_case.execute(current_user.id, payload, ai_service)
    except QuizServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return {"questions": questions}

@router.post("/evaluate-answer")
@limiter.limit(AI_RATE_LIMIT)
def evaluate_answer_endpoint(
    request: Request,
    payload: EvaluationRequest,
    current_user: Student = Depends(get_current_user),
    _quota: None = Depends(enforce_ai_quota),
    use_case: EvaluateAnswerUseCasePort = Depends(get_evaluate_answer_use_case),
    ai_service: QuizAIServicePort = Depends(get_eval_ai_service)
):
    try:
        return use_case.execute(current_user.id, payload, ai_service)
    except QuizServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@router.post("/quiz/result")
def save_quiz_result(
    result: QuizResultCreate,
    current_user: Student = Depends(get_current_user),
    use_case: SaveQuizResultUseCasePort = Depends(get_save_quiz_result_use_case)
):
    try:
        use_case.execute(current_user.id, result)
    except QuizServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return {"status": "saved"}
