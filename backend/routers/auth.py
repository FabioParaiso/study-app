from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas.student import StudentCreate, StudentLogin
from slowapi import Limiter
from slowapi.util import get_remote_address
from security import create_access_token
from services.auth_service import AuthService, AuthServiceError
from services.ports import StudentAuthRepositoryPort
from dependencies import get_student_repo

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

def get_auth_service(repo: StudentAuthRepositoryPort = Depends(get_student_repo)):
    return AuthService(repo)

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
def register_student(request: Request, student_data: StudentCreate, auth_service: AuthService = Depends(get_auth_service)):
    try:
        student = auth_service.register(student_data.name, student_data.password)
    except AuthServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    
    # Auto-login after register
    access_token = create_access_token(data={"sub": str(student.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": _student_to_response(student)
    }

@router.post("/login")
@limiter.limit("5/minute")
def login_student(request: Request, student_data: StudentLogin, auth_service: AuthService = Depends(get_auth_service)):
    try:
        student = auth_service.login(student_data.name, student_data.password)
    except AuthServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    
    access_token = create_access_token(data={"sub": str(student.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": _student_to_response(student)
    }
