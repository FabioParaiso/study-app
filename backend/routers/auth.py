from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from repositories.study_repository import StudyRepository
from schemas.base import StudentCreate
from database import get_db

router = APIRouter()

def get_repository(db: Session = Depends(get_db)):
    return StudyRepository(db)

@router.post("/students")
def login_student(student_data: StudentCreate, repo: StudyRepository = Depends(get_repository)):
    student = repo.get_or_create_student(student_data.name)
    return {"id": student.id, "name": student.name}
