from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from repositories.student_repository import StudentRepository
from schemas.student import StudentCreate
from database import get_db

router = APIRouter()

def get_student_repo(db: Session = Depends(get_db)):
    return StudentRepository(db)

@router.post("/students")
def login_student(student_data: StudentCreate, repo: StudentRepository = Depends(get_student_repo)):
    student = repo.get_or_create_student(student_data.name)
    return {
        "id": student.id, 
        "name": student.name,
        "total_xp": student.total_xp,
        "current_avatar": student.current_avatar,
        "high_score": student.high_score
    }
