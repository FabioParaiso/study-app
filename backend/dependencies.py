from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from repositories.student_repository import (
    StudentAuthRepository,
    StudentGamificationRepository,
    StudentLookupRepository,
)
from modules.auth.ports import StudentLookupRepositoryPort
from modules.common.ports import TokenServicePort
from services.token_service import TokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_student_auth_repo(db=Depends(get_db)):
    return StudentAuthRepository(db)


def get_student_lookup_repo(db=Depends(get_db)):
    return StudentLookupRepository(db)


def get_student_gamification_repo(db=Depends(get_db)):
    return StudentGamificationRepository(db)


def get_token_service():
    return TokenService()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: StudentLookupRepositoryPort = Depends(get_student_lookup_repo),
    token_service: TokenServicePort = Depends(get_token_service)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = token_service.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    student_id = payload.get("sub")
    if student_id is None:
        raise credentials_exception
        
    student = repo.get_student(int(student_id))
    if student is None:
        raise credentials_exception
        
    return student
