from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from repositories.student_repository import StudentRepository
from schemas.gamification import XPUpdate, AvatarUpdate, HighScoreUpdate

router = APIRouter()

def get_repo(db: Session = Depends(get_db)):
    return StudentRepository(db)

@router.post("/gamification/xp")
def add_xp(data: XPUpdate, repo: StudentRepository = Depends(get_repo)):
    student = repo.update_xp(data.student_id, data.amount)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"total_xp": student.total_xp}

@router.post("/gamification/avatar")
def update_avatar(data: AvatarUpdate, repo: StudentRepository = Depends(get_repo)):
    student = repo.update_avatar(data.student_id, data.avatar)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"current_avatar": student.current_avatar}

@router.post("/gamification/highscore")
def update_high_score(data: HighScoreUpdate, repo: StudentRepository = Depends(get_repo)):
    student = repo.update_high_score(data.student_id, data.score)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"high_score": student.high_score}
