from pydantic import BaseModel, field_validator
from typing import List, Optional
import re

class QuizRequest(BaseModel):
    text: Optional[str] = None
    use_saved: bool = False
    topics: list[str] = []
    api_key: Optional[str] = None
    quiz_type: str = "multiple"

    @field_validator('topics')
    @classmethod
    def validate_topics(cls, v):
        # We might not even need this validation if topics are extracted by AI on the backend
        # But if the frontend sends topics (e.g. edit mode), we should validate structure.
        # However, for now, the `topics` field in QuizRequest is likely used for filtering?
        # Let's check usage. 
        # Actually, QuizRequest.topics seems to be used for GENERATION hints or filtering.
        # If we are changing to concepts, we might need 'concept_ids' or similar.
        # For now, let's keep it as string list for backward compatibility or simple filtering.
        return v


class AnalyticsItem(BaseModel):
    topic: str # Keeping 'topic' name for frontend compatibility, but this will now hold Concept Name
    concept_id: Optional[int] = None # Link to the specific concept
    is_correct: bool

class QuizResultCreate(BaseModel):
    score: int
    total_questions: int
    quiz_type: str
    detailed_results: List[AnalyticsItem]
    # student_id removed
    study_material_id: Optional[int] = None # NEW: Explicit link
    xp_earned: int = 0

class AnalyzeRequest(BaseModel):
    pass # No fields left if we remove student_id, but wait, usually AnalyzeRequest needs something?
    # Checking previous file view: 'data' was loaded from repo based on student_id. 
    # If the request body was ONLY student_id, now it's empty.
    # Pydantic models with no fields are fine, but let's check content.

class EvaluationRequest(BaseModel):
    question: str
    user_answer: str
    quiz_type: str = "open-ended" # "open-ended" or "short_answer"
    api_key: Optional[str] = None
