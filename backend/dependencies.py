from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from security import decode_access_token
from repositories.student_repository import StudentRepository
from services.ports import StudentLookupRepositoryPort

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_student_repo(db = Depends(get_db)):
    return StudentRepository(db)


def get_current_user(token: str = Depends(oauth2_scheme), repo: StudentLookupRepositoryPort = Depends(get_student_repo)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    student_id = payload.get("sub")
    if student_id is None:
        raise credentials_exception
        
    student = repo.get_student(int(student_id))
    if student is None:
        raise credentials_exception
        
    return student
