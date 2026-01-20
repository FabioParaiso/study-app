from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import List, Optional
import os
import re
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.orm import Session

# Dependency Injection Imports
import sys
from pathlib import Path

# Add backend directory to sys.path to allow imports from 'services'
sys.path.append(str(Path(__file__).parent))

from services.document_service import DocumentService
from services.topic_service import TopicService
from services.ai_service import AIService
from services.analytics_service import AnalyticsService
from repositories.study_repository import StudyRepository
from database import get_db, engine
import models

# Create Tables
models.Base.metadata.create_all(bind=engine)

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependencies ---
def get_repository(db: Session = Depends(get_db)):
    return StudyRepository(db)

def get_ai_service(api_key: str = None):
    # If API key is not passed, try env
    key = api_key or os.getenv("OPENAI_API_KEY")
    return AIService(key)

# --- Models ---
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

# --- Endpoints ---



@app.get("/health")
def health_check():
    return {"status": "ok"}

# Student Endpoints
@app.post("/students")
def login_student(student_data: StudentCreate, repo: StudyRepository = Depends(get_repository)):
    student = repo.get_or_create_student(student_data.name)
    return {"id": student.id, "name": student.name}

# Study Material Endpoints
@app.get("/current-material")
def get_current_material(student_id: int, repo: StudyRepository = Depends(get_repository)):
    data = repo.load(student_id)
    if data:
        return {
            "has_material": True, 
            "source": data.get("source"), 
            "preview": data.get("text")[:200] if data.get("text") else "",
            "topics": data.get("topics", [])
        }
    return {"has_material": False}

@app.post("/clear-material")
def clear_material(student_id: int, repo: StudyRepository = Depends(get_repository)):
    repo.clear(student_id)
    return {"status": "cleared"}

@app.post("/upload")
async def upload_file(
    student_id: int = Form(...),
    file: UploadFile = File(...), 
    repo: StudyRepository = Depends(get_repository)
):
    try:
        # Security Check: File Size Limit
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

        content = await file.read()
        file_type = file.content_type
        
        if not file_type:
             if file.filename.endswith('.pdf'):
                 file_type = 'application/pdf'
             else:
                 file_type = 'text/plain'

        # 1. Extract Text
        text = DocumentService.extract_text(content, file_type)
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text from file.")

        # 2. Extract Topics (AI + Deduplication)
        # Note: We prioritize headers but now use LLM to semantic deduplication
        
        # Get services
        ai_service = get_ai_service()
        existing_topics = repo.get_all_topics(student_id)
        
        topics = TopicService.extract_topics(text, ai_service, existing_topics)

        # 3. Save
        repo.save(student_id, text, file.filename, topics)
        
        return {"text": text, "filename": file.filename, "topics": topics}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/analyze-topics")
def analyze_topics_endpoint(
    request: AnalyzeRequest,
    repo: StudyRepository = Depends(get_repository)
):
    data = repo.load(request.student_id)
    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found to analyze")

    text = data.get("text")
    source = data.get("source")
    
    # Re-analyze (AI + Deduplication)
    ai_service = get_ai_service()
    existing_topics = repo.get_all_topics(request.student_id)

    topics = TopicService.extract_topics(text, ai_service, existing_topics)
    
    # Update storage
    repo.save(request.student_id, text, source, topics)
    
    return {"topics": topics}

@app.post("/generate-quiz")
def generate_quiz_endpoint(
    request: QuizRequest,
    repo: StudyRepository = Depends(get_repository)
):
    # Ensure student_id is present (it should be optional in model but logic requires it now for context)
    if not request.student_id:
         raise HTTPException(status_code=400, detail="Student ID is required.")

    data = repo.load(request.student_id)
    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found. Upload a file first.")
    
    text = data.get("text")
    
    # Initialize AI Service with key
    ai_service = get_ai_service(request.api_key)
    if not ai_service.client:
         raise HTTPException(status_code=400, detail="API Key is required for quiz generation.")

    # Adaptive Logic: If student_id is provided, prioritize weak points
    priority_topics = []
    if request.student_id:
        analytics_service = AnalyticsService(repo)
        priority_topics = analytics_service.get_adaptive_topics(request.student_id)

    # Combine request topics with priority topics
    # Logic: If request topics are specified (e.g. by filter), use them.
    # If "All" (empty list), use adaptive priority topics + general.
    target_topics = request.topics
    if not target_topics and priority_topics:
        target_topics = priority_topics

    if request.quiz_type == "open-ended":
        questions = ai_service.generate_open_questions(text, target_topics)
    else:
        questions = ai_service.generate_quiz(text, target_topics)
    
    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate quiz. Please try again.")
        
    return {"questions": questions}

@app.post("/evaluate-answer")
def evaluate_answer_endpoint(
    request: EvaluationRequest,
    repo: StudyRepository = Depends(get_repository)
):
    # Determine student context (add student_id to EvaluationRequest model if not there, wait, I need to check model again or just add it)
    # The user is logged in on frontend, so we expect student_id.
    
    # Correction: I need to adding student_id to EvaluationRequest model first, but I can't do two edits in one replace.
    # I'll assuming I will add it or have added it. Actually I haven't added it to EvaluationRequest yet.
    # Let me do that in a separate step or just rely on an update.
    # For now, let's look at the implementation assuming request.student_id exists.
    
    if hasattr(request, 'student_id') and request.student_id:
         data = repo.load(request.student_id)
    else:
         # Fallback or Error
         # Since I control the model, I'll enforce it.
         raise HTTPException(status_code=400, detail="Student ID required for evaluation context.")

    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found.")
        
    text = data.get("text")
    
    ai_service = get_ai_service(request.api_key)
    if not ai_service.client:
         raise HTTPException(status_code=400, detail="API Key is required for evaluation.")
         
    result = ai_service.evaluate_answer(text, request.question, request.user_answer)
    return result

@app.post("/quiz/result")
def save_quiz_result(
    result: QuizResultCreate,
    repo: StudyRepository = Depends(get_repository)
):
    # Determine current material ID if possible
    current = repo.load()
    material_id = current["id"] if current else None

    # Convert Pydantic items to dicts
    analytics_data = [item.dict() for item in result.detailed_results]

    success = repo.save_quiz_result(
        student_id=result.student_id,
        score=result.score,
        total=result.total_questions,
        quiz_type=result.quiz_type,
        analytics_data=analytics_data,
        material_id=material_id
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save results")
    return {"status": "saved"}

@app.get("/analytics/weak-points")
def get_weak_points(
    student_id: int,
    repo: StudyRepository = Depends(get_repository)
):
    analytics = AnalyticsService(repo)
    return analytics.get_weak_points(student_id)
