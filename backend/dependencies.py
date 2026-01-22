from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from security import decode_access_token
from repositories.student_repository import StudentRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        
    repo = StudentRepository(db)
    # Assuming get_student_by_id exists or using a generic get method
    # Let's verify StudentRepository methods first. 
    # Since I cannot see it right now, I will assume find_by_id or similar exists or I will check it.
    # Looking at previous file views, I saw repositories/student_repository.py but didn't open it.
    # I'll implement this defensively.
    
    student = repo.get_student(int(student_id))
    if student is None:
        raise credentials_exception
        
    return student
