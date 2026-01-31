from fastapi import APIRouter, Depends, HTTPException, status, Request
import hmac
import os
from schemas.student import StudentCreate, StudentLogin
from rate_limiter import limiter
from modules.auth.service import AuthService, AuthServiceError
from modules.auth.ports import AuthServicePort, StudentAuthRepositoryPort
from modules.common.ports import TokenServicePort
from dependencies import get_student_auth_repo, get_token_service

router = APIRouter()

def get_auth_service(repo: StudentAuthRepositoryPort = Depends(get_student_auth_repo)):
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
def register_student(
    request: Request,
    student_data: StudentCreate,
    auth_service: AuthServicePort = Depends(get_auth_service),
    token_service: TokenServicePort = Depends(get_token_service)
):
    register_enabled = os.getenv("REGISTER_ENABLED", "true").strip().lower() not in {"0", "false", "no", "off"}
    if not register_enabled:
        raise HTTPException(status_code=403, detail="Registo desativado.")

    invite_code = os.getenv("INVITE_CODE")
    if invite_code:
        if not student_data.invite_code or not hmac.compare_digest(student_data.invite_code, invite_code):
            raise HTTPException(status_code=403, detail="Invite code invalido.")
    try:
        student = auth_service.register(student_data.name, student_data.password)
    except AuthServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    
    # Auto-login after register
    access_token = token_service.create_access_token(data={"sub": str(student.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": _student_to_response(student)
    }

@router.post("/login")
@limiter.limit("5/minute")
def login_student(
    request: Request,
    student_data: StudentLogin,
    auth_service: AuthServicePort = Depends(get_auth_service),
    token_service: TokenServicePort = Depends(get_token_service)
):
    try:
        student = auth_service.login(student_data.name, student_data.password)
    except AuthServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    
    access_token = token_service.create_access_token(data={"sub": str(student.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": _student_to_response(student)
    }
