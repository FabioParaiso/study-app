from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from repositories.student_repository import StudentRepository
from schemas.student import StudentCreate, StudentLogin
from database import get_db
from slowapi import Limiter
from slowapi.util import get_remote_address
from security import create_access_token

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

def get_student_repo(db: Session = Depends(get_db)):
    return StudentRepository(db)

def _student_to_response(student) -> dict:
    """Helper to convert Student model to API response dict (DRY)."""
    return {
        "id": student.id, 
        "name": student.name,
        "total_xp": student.total_xp,
        "current_avatar": student.current_avatar,
        "high_score": student.high_score
    }

@router.post("/register")
@limiter.limit("5/minute")
def register_student(request: Request, student_data: StudentCreate, repo: StudentRepository = Depends(get_student_repo)):
    student = repo.create_student(student_data.name, student_data.password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Esse nome já existe. Tenta fazer Login ou escolhe outro nome."
        )
    
    # Auto-login after register
    access_token = create_access_token(data={"sub": str(student.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": _student_to_response(student)
    }

@router.post("/login")
@limiter.limit("5/minute")
def login_student(request: Request, student_data: StudentLogin, repo: StudentRepository = Depends(get_student_repo)):
    student = repo.authenticate_student(student_data.name, student_data.password)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas. Verifica o nome e a password."
        )
    
    access_token = create_access_token(data={"sub": str(student.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": _student_to_response(student)
    }

