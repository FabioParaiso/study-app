from pydantic import BaseModel, field_validator
from typing import List, Optional
import re

class StudentCreate(BaseModel):
    name: str

class QuizRequest(BaseModel):
    text: Optional[str] = None
    use_saved: bool = False
    topics: list[str] = []
    api_key: Optional[str] = None
    quiz_type: str = "multiple"
    student_id: Optional[int] = None

    @field_validator('topics')
    @classmethod
    def validate_topics(cls, v):
        if len(v) > 20:
            raise ValueError('Too many topics (max 20)')

        for topic in v:
            if len(topic) > 100:
                raise ValueError(f'Topic too long: {topic[:20]}... (max 100 chars)')

            if re.search(r'[\n\r\t]', topic):
                raise ValueError('Topics cannot contain control characters (newlines, tabs)')

            if re.search(r'[<>{}\[\]]', topic):
                raise ValueError('Topics cannot contain special brackets < > { } [ ]')

        return v

class AnalyticsItem(BaseModel):
    topic: str
    is_correct: bool

class QuizResultCreate(BaseModel):
    score: int
    total_questions: int
    quiz_type: str
    detailed_results: List[AnalyticsItem]
    student_id: int

class AnalyzeRequest(BaseModel):
    student_id: int

class EvaluationRequest(BaseModel):
    student_id: int
    question: str
    user_answer: str
    api_key: Optional[str] = None
