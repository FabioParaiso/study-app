from pydantic import BaseModel, field_validator
from typing import List, Optional, Literal
import re

QuizType = Literal["multiple-choice", "short_answer", "open-ended"]
EvaluationQuizType = Literal["short_answer", "open-ended"]

class QuizRequest(BaseModel):
    text: Optional[str] = None
    use_saved: bool = False
    topics: list[str] = []
    api_key: Optional[str] = None
    quiz_type: QuizType = "multiple-choice"

    @field_validator('topics')
    @classmethod
    def validate_topics(cls, v):
        for topic in v:
            if len(topic) > 100:
                raise ValueError("Topic too long (max 100 chars)")
            if re.search(r"[\n\r]", topic):
                raise ValueError("Topic contains control characters") 
            if re.search(r"[{}]", topic):
                raise ValueError("Topic contains special brackets")
        return v


class AnalyticsItem(BaseModel):
    topic: str # Keeping 'topic' name for frontend compatibility, but this will now hold Concept Name
    concept_id: Optional[int] = None # Link to the specific concept
    is_correct: bool

class QuizResultCreate(BaseModel):
    score: int
    total_questions: int
    quiz_type: QuizType
    detailed_results: List[AnalyticsItem]
    # student_id removed
    study_material_id: Optional[int] = None # NEW: Explicit link
    xp_earned: int = 0
    duration_seconds: int = 0
    active_seconds: int = 0

class AnalyzeRequest(BaseModel):
    pass # No fields left if we remove student_id, but wait, usually AnalyzeRequest needs something?
    # Checking previous file view: 'data' was loaded from repo based on student_id. 
    # If the request body was ONLY student_id, now it's empty.
    # Pydantic models with no fields are fine, but let's check content.

class EvaluationRequest(BaseModel):
    question: str
    user_answer: str
    quiz_type: EvaluationQuizType = "open-ended" # "open-ended" or "short_answer"
    api_key: Optional[str] = None
