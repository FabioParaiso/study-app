from fastapi import APIRouter, Depends, HTTPException
from schemas.gamification import XPUpdate, AvatarUpdate, HighScoreUpdate
from dependencies import get_current_user, get_student_repo
from models import Student
from services.gamification_service import GamificationService, GamificationServiceError
from services.ports import StudentGamificationRepositoryPort

router = APIRouter()

def get_gamification_service(repo: StudentGamificationRepositoryPort = Depends(get_student_repo)):
    return GamificationService(repo)

@router.post("/gamification/xp")
def add_xp(data: XPUpdate, current_user: Student = Depends(get_current_user), service: GamificationService = Depends(get_gamification_service)):
    # Ignore data.student_id, use authenticated user
    try:
        student = service.add_xp(current_user.id, data.amount)
    except GamificationServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return {"total_xp": student.total_xp}

@router.post("/gamification/avatar")
def update_avatar(data: AvatarUpdate, current_user: Student = Depends(get_current_user), service: GamificationService = Depends(get_gamification_service)):
    # Ignore data.student_id, use authenticated user
    try:
        student = service.update_avatar(current_user.id, data.avatar)
    except GamificationServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return {"current_avatar": student.current_avatar}

@router.post("/gamification/highscore")
def update_high_score(data: HighScoreUpdate, current_user: Student = Depends(get_current_user), service: GamificationService = Depends(get_gamification_service)):
    # Ignore data.student_id, use authenticated user
    try:
        student = service.update_high_score(current_user.id, data.score)
    except GamificationServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    return {"high_score": student.high_score}
