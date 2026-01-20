from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import os
import asyncio
from database import get_db
from repositories.study_repository import StudyRepository
from services.document_service import DocumentService
from services.topic_service import TopicService
from services.ai_service import AIService
from services.quiz_strategies import MultipleChoiceStrategy, OpenEndedStrategy
from services.analytics_service import AnalyticsService
from schemas.base import QuizRequest, AnalyzeRequest, EvaluationRequest, QuizResultCreate

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

# --- Dependencies ---
def get_repository(db: Session = Depends(get_db)):
    return StudyRepository(db)

def get_ai_service(api_key: str = None):
    # If API key is not passed, try env
    key = api_key or os.getenv("OPENAI_API_KEY")
    return AIService(key)

# --- Endpoints ---

@router.get("/current-material")
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

@router.post("/clear-material")
def clear_material(student_id: int, repo: StudyRepository = Depends(get_repository)):
    repo.clear(student_id)
    return {"status": "cleared"}

@router.post("/upload")
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
        # Offload blocking CPU operation to a thread
        text = await asyncio.to_thread(DocumentService.extract_text, content, file_type)
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text from file.")

        # 2. Extract Topics (AI + Deduplication)
        ai_service = get_ai_service()
        existing_topics = repo.get_all_topics(student_id)
        
        # Offload blocking API call to a thread
        topics = await asyncio.to_thread(TopicService.extract_topics, text, ai_service, existing_topics)

        # 3. Save
        repo.save(student_id, text, file.filename, topics)
        
        return {"text": text, "filename": file.filename, "topics": topics}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/analyze-topics")
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

@router.post("/generate-quiz")
def generate_quiz_endpoint(
    request: QuizRequest,
    repo: StudyRepository = Depends(get_repository)
):
    if not request.student_id:
         raise HTTPException(status_code=400, detail="Student ID is required.")

    data = repo.load(request.student_id)
    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found. Upload a file first.")
    
    text = data.get("text")
    
    ai_service = get_ai_service(request.api_key)
    if not ai_service.client:
         raise HTTPException(status_code=400, detail="API Key is required for quiz generation.")

    # Adaptive Logic
    priority_topics = []
    if request.student_id:
        analytics_service = AnalyticsService(repo)
        priority_topics = analytics_service.get_adaptive_topics(request.student_id)

    target_topics = request.topics
    if not target_topics and priority_topics:
        target_topics = priority_topics

    if request.quiz_type == "open-ended":
        strategy = OpenEndedStrategy()
    else:
        strategy = MultipleChoiceStrategy()

    questions = ai_service.generate_quiz(strategy, text, target_topics, priority_topics)
    
    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate quiz. Please try again.")
        
    return {"questions": questions}

@router.post("/evaluate-answer")
def evaluate_answer_endpoint(
    request: EvaluationRequest,
    repo: StudyRepository = Depends(get_repository)
):
    # Note: request.student_id is required by schema now
    data = repo.load(request.student_id)

    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found.")
        
    text = data.get("text")
    
    ai_service = get_ai_service(request.api_key)
    if not ai_service.client:
         raise HTTPException(status_code=400, detail="API Key is required for evaluation.")
         
    result = ai_service.evaluate_answer(text, request.question, request.user_answer)
    return result

@router.post("/quiz/result")
def save_quiz_result(
    result: QuizResultCreate,
    repo: StudyRepository = Depends(get_repository)
):
    current = repo.load(result.student_id) # Should load by student ID to get their current material? 
    # Actually repo.load takes student_id defaults to None which might be issue if not passed.
    # repo.load(student_id) loads that student's material.
    
    material_id = current["id"] if current else None

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

@router.get("/analytics/weak-points")
def get_weak_points(
    student_id: int,
    repo: StudyRepository = Depends(get_repository)
):
    analytics = AnalyticsService(repo)
    return analytics.get_weak_points(student_id)
