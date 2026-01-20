from pydantic import BaseModel

class XPUpdate(BaseModel):
    student_id: int
    amount: int

class AvatarUpdate(BaseModel):
    student_id: int
    avatar: str

class HighScoreUpdate(BaseModel):
    student_id: int
    score: int
