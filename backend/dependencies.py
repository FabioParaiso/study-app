from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from repositories.student_repository import (
    StudentAuthRepository,
    StudentGamificationRepository,
    StudentLookupRepository,
)
from repositories.usage_repository import DailyUsageRepository
from modules.challenges.repository import ChallengeRepository
from modules.challenges.service import ChallengeService
from modules.auth.ports import StudentLookupRepositoryPort
from modules.common.ports import TokenServicePort
from modules.challenges.ports import ChallengeServicePort
from services.token_service import TokenService
from services.usage_service import UsageService, UsageLimitReached

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_student_auth_repo(db=Depends(get_db)):
    return StudentAuthRepository(db)


def get_student_lookup_repo(db=Depends(get_db)):
    return StudentLookupRepository(db)


def get_student_gamification_repo(db=Depends(get_db)):
    return StudentGamificationRepository(db)


def get_token_service():
    return TokenService()


def get_usage_repo(db=Depends(get_db)):
    return DailyUsageRepository(db)


def get_usage_service(repo=Depends(get_usage_repo)):
    return UsageService(repo)


def get_challenge_repo(db=Depends(get_db)):
    return ChallengeRepository(db)


def get_challenge_service(repo=Depends(get_challenge_repo)) -> ChallengeServicePort:
    return ChallengeService(repo)


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


def enforce_ai_quota(
    current_user=Depends(get_current_user),
    usage_service: UsageService = Depends(get_usage_service),
):
    try:
        usage_service.check_and_increment(current_user.id)
    except UsageLimitReached as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Limite diario atingido ({exc.limit}/dia).",
        )
