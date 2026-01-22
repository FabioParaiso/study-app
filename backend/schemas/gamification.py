from pydantic import BaseModel
from typing import Optional

class XPUpdate(BaseModel):
    amount: int

class AvatarUpdate(BaseModel):
    avatar: str

class HighScoreUpdate(BaseModel):
    score: int
