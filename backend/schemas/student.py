from pydantic import BaseModel, Field, field_validator
import re

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Nome do aluno")
    password: str = Field(..., description="Password (8+ chars, 1 upper, 1 lower, 1 digit, 1 special)")

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[@$!%*?&]', v):
            # Optional: Allow broader special chars or strictly these
            raise ValueError('Password must contain at least one special character (@$!%*?&)')
        return v

class StudentLogin(BaseModel):
    name: str = Field(..., min_length=2, max_length=30)
    password: str = Field(..., min_length=4, max_length=72)
