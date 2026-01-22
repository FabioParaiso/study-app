from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from repositories.student_repository import StudentRepository
from schemas.gamification import XPUpdate, AvatarUpdate, HighScoreUpdate
from dependencies import get_current_user
from models import Student

router = APIRouter()

def get_repo(db: Session = Depends(get_db)):
    return StudentRepository(db)

@router.post("/gamification/xp")
def add_xp(data: XPUpdate, current_user: Student = Depends(get_current_user), repo: StudentRepository = Depends(get_repo)):
    # Ignore data.student_id, use authenticated user
    student = repo.update_xp(current_user.id, data.amount)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"total_xp": student.total_xp}

@router.post("/gamification/avatar")
def update_avatar(data: AvatarUpdate, current_user: Student = Depends(get_current_user), repo: StudentRepository = Depends(get_repo)):
    # Ignore data.student_id, use authenticated user
    student = repo.update_avatar(current_user.id, data.avatar)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"current_avatar": student.current_avatar}

@router.post("/gamification/highscore")
def update_high_score(data: HighScoreUpdate, current_user: Student = Depends(get_current_user), repo: StudentRepository = Depends(get_repo)):
    # Ignore data.student_id, use authenticated user
    student = repo.update_high_score(current_user.id, data.score)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"high_score": student.high_score}
