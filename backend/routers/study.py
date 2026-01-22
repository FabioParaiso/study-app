from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import os
import random
import asyncio
from database import get_db
from repositories.material_repository import MaterialRepository
from repositories.quiz_repository import QuizRepository
from services.document_service import DocumentService
from services.topic_service import TopicService
from services.ai_service import AIService
from services.quiz_strategies import MultipleChoiceStrategy, OpenEndedStrategy, ShortAnswerStrategy
from services.analytics_service import AnalyticsService
from schemas.study import QuizRequest, AnalyzeRequest, EvaluationRequest, QuizResultCreate
from dependencies import get_current_user
from models import Student

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

# --- Dependencies ---
def get_material_repo(db: Session = Depends(get_db)):
    return MaterialRepository(db)

def get_quiz_repo(db: Session = Depends(get_db)):
    return QuizRepository(db)

def get_ai_service(api_key: str = None):
    # If API key is not passed, try env
    key = api_key or os.getenv("OPENAI_API_KEY")
    return AIService(key)

# --- Endpoints ---

@router.get("/current-material")
def get_current_material(current_user: Student = Depends(get_current_user), repo: MaterialRepository = Depends(get_material_repo)):
    data = repo.load(current_user.id)
    if data:
        return {
            "has_material": True,
            "id": data.get("id"),  # CRITICAL: Frontend needs this.
            "source": data.get("source"), 
            "preview": data.get("text")[:200] if data.get("text") else "",
            "topics": data.get("topics", []),
            # Gamification stats for this material
            "total_xp": data.get("total_xp", 0),
            "high_score": data.get("high_score", 0)
        }
    return {"has_material": False}

@router.post("/clear-material")
def clear_material(current_user: Student = Depends(get_current_user), repo: MaterialRepository = Depends(get_material_repo)):
    repo.clear(current_user.id)
    return {"status": "cleared"}

@router.get("/materials")
def list_materials(current_user: Student = Depends(get_current_user), repo: MaterialRepository = Depends(get_material_repo)):
    return repo.list_all(current_user.id)

@router.post("/materials/{material_id}/activate")
def activate_material(material_id: int, current_user: Student = Depends(get_current_user), repo: MaterialRepository = Depends(get_material_repo)):
    success = repo.activate(current_user.id, material_id)
    if not success:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"status": "activated"}

def get_document_service():
    return DocumentService()

def get_topic_service():
    return TopicService()

@router.post("/upload")
async def upload_file(
    current_user: Student = Depends(get_current_user),
    file: UploadFile = File(...), 
    repo: MaterialRepository = Depends(get_material_repo),
    quiz_repo: QuizRepository = Depends(get_quiz_repo),
    doc_service: DocumentService = Depends(get_document_service),
    topic_service: TopicService = Depends(get_topic_service)
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
        # Optimization: Offload blocking PDF/Text extraction to threadpool to prevent blocking event loop
        text = await asyncio.to_thread(doc_service.extract_text, content, file_type)
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text from file.")

        # 2. Extract Topics (AI + Deduplication)
        ai_service = get_ai_service()
        existing_topics = quiz_repo.get_all_topics(current_user.id)
        
        # Optimization: Offload blocking AI network call to threadpool
        topics = await asyncio.to_thread(topic_service.extract_topics, text, ai_service, existing_topics)

        # 3. Save
        repo.save(current_user.id, text, file.filename, topics)
        
        return {"text": text, "filename": file.filename, "topics": topics}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/analyze-topics")
def analyze_topics_endpoint(
    request: AnalyzeRequest,
    current_user: Student = Depends(get_current_user),
    repo: MaterialRepository = Depends(get_material_repo),
    quiz_repo: QuizRepository = Depends(get_quiz_repo),
    topic_service: TopicService = Depends(get_topic_service)
):
    # Ignore request.student_id, use token
    data = repo.load(current_user.id)
    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found to analyze")

    text = data.get("text")
    source = data.get("source")
    
    # Re-analyze (AI + Deduplication)
    ai_service = get_ai_service()
    existing_topics = quiz_repo.get_all_topics(current_user.id)

    topics = topic_service.extract_topics(text, ai_service, existing_topics)
    
    # Update storage
    repo.save(current_user.id, text, source, topics)
    
    return {"topics": topics}

@router.post("/generate-quiz")
def generate_quiz_endpoint(
    request: QuizRequest,
    current_user: Student = Depends(get_current_user),
    repo: MaterialRepository = Depends(get_material_repo),
    quiz_repo: QuizRepository = Depends(get_quiz_repo)
):
    # request.student_id is ignored
    data = repo.load(current_user.id)
    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found. Upload a file first.")
    
    text = data.get("text")
    
    ai_service = get_ai_service(request.api_key)
    if not ai_service.client:
         raise HTTPException(status_code=400, detail="API Key is required for quiz generation.")

    # Adaptive Logic
    priority_topics = []
    
    analytics_service = AnalyticsService(quiz_repo)
    # Scope adaptive learning to the current material
    material_id = data.get("id")
    adaptive_data = analytics_service.get_adaptive_topics(current_user.id, material_id)
    # Extract topics from "boost" (weak points) and "mastered" (for review)
    # We prioritize boost, but can also include some mastered for spaced repetition
    if adaptive_data:
            priority_topics = adaptive_data.get("boost", []) + adaptive_data.get("mastered", [])

    target_topics = request.topics
    
    # If user explicitly selected topics, don't add priority_topics to avoid conflicting instructions
    # Priority topics (adaptive learning) only apply when user selects "all topics"
    if target_topics:
        priority_topics = []  # Clear - user selection takes absolute precedence
    elif priority_topics:
        target_topics = priority_topics  # Fallback to adaptive if no explicit selection

    material_xp = data.get("total_xp", 0)

    if request.quiz_type == "open-ended":
        if material_xp < 900:
             raise HTTPException(status_code=403, detail="Level Locked. Requires 900 XP.")
        strategy = OpenEndedStrategy()
    elif request.quiz_type == "short_answer":
        if material_xp < 300:
             raise HTTPException(status_code=403, detail="Level Locked. Requires 300 XP.")
        strategy = ShortAnswerStrategy()
    else:
        strategy = MultipleChoiceStrategy()

    material_topics = data.get("topics", [])

    questions = ai_service.generate_quiz(strategy, text, target_topics, priority_topics, material_topics)
    
    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate quiz. Please try again.")
    
    # Randomize options for multiple choice questions
    if request.quiz_type == "multiple-choice" or not request.quiz_type:
        for question in questions:
            if "options" in question and "correctIndex" in question:
                # Store the correct answer
                correct_answer = question["options"][question["correctIndex"]]
                
                # Shuffle the options
                random.shuffle(question["options"])
                
                # Update correctIndex to the new position of the correct answer
                question["correctIndex"] = question["options"].index(correct_answer)
        
    return {"questions": questions}

@router.post("/evaluate-answer")
def evaluate_answer_endpoint(
    request: EvaluationRequest,
    current_user: Student = Depends(get_current_user),
    repo: MaterialRepository = Depends(get_material_repo)
):
    # request.student_id is ignored
    data = repo.load(current_user.id)

    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found.")
        
    text = data.get("text")
    
    ai_service = get_ai_service(request.api_key)
    if not ai_service.client:
         raise HTTPException(status_code=400, detail="API Key is required for evaluation.")
         
    result = ai_service.evaluate_answer(text, request.question, request.user_answer, request.quiz_type)
    return result

@router.post("/quiz/result")
def save_quiz_result(
    result: QuizResultCreate,
    current_user: Student = Depends(get_current_user),
    repo: QuizRepository = Depends(get_quiz_repo),
    material_repo: MaterialRepository = Depends(get_material_repo)
):
    # Use explicit ID from frontend, or fallback to active if missing
    material_id = result.study_material_id
    if not material_id:
        current = material_repo.load(current_user.id) 
        material_id = current["id"] if current else None

    analytics_data = [item.dict() for item in result.detailed_results]

    success = repo.save_quiz_result(
        student_id=current_user.id,
        score=result.score,
        total=result.total_questions,
        quiz_type=result.quiz_type,
        analytics_data=analytics_data,
        material_id=material_id,
        xp_earned=result.xp_earned
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save results")
    return {"status": "saved"}

@router.get("/analytics/weak-points")
def get_weak_points(
    current_user: Student = Depends(get_current_user),
    material_id: int = None,
    repo: QuizRepository = Depends(get_quiz_repo),
    material_repo: MaterialRepository = Depends(get_material_repo)
):
    student_id = current_user.id
    if not material_id:
        current = material_repo.load(student_id)
        if not current:
            return []
        material_id = current["id"]
    
    analytics = AnalyticsService(repo)
    result = analytics.get_weak_points(student_id, material_id)
    return result
