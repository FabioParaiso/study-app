from fastapi import APIRouter, Depends
from modules.analytics.deps import get_quiz_service
from modules.quizzes.service import QuizService
from dependencies import get_current_user
from models import Student

router = APIRouter()

# --- Endpoints ---
@router.get("/analytics/weak-points")
def get_weak_points(
    current_user: Student = Depends(get_current_user),
    material_id: int | None = None,
    quiz_service: QuizService = Depends(get_quiz_service)
):
    return quiz_service.get_weak_points(current_user.id, material_id)
