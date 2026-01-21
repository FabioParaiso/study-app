from pydantic import BaseModel, Field

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Nome do aluno")
    password: str = Field(..., min_length=4, max_length=72, description="Password (4-72 caracteres)")

class StudentLogin(BaseModel):
    name: str = Field(..., min_length=2, max_length=30)
    password: str = Field(..., min_length=4, max_length=72)
