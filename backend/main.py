from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from logic import extract_text_from_file, generate_quiz, extract_topics, generate_open_questions, evaluate_answer
from storage import save_study_material, load_study_material, clear_study_material
from io import BytesIO
from pypdf import PdfReader
import json

from pathlib import Path
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

class QuizRequest(BaseModel):
    text: Optional[str] = None
    use_saved: bool = False
    topics: list[str] = []
    api_key: Optional[str] = None
    quiz_type: str = "multiple"

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/current-material")
def get_current_material():
    data = load_study_material()
    if data:
        return {
            "has_material": True, 
            "source": data.get("source"), 
            "preview": data.get("text")[:200],
            "topics": data.get("topics", [])
        }
    return {"has_material": False}

@app.post("/clear-material")
def clear_material():
    clear_study_material()
    return {"status": "cleared"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Security Check: File Size Limit
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

        content = await file.read()
        file_type = file.content_type
        text = ""

        if not file_type:
             if file.filename.endswith('.pdf'):
                 file_type = 'application/pdf'
             else:
                 file_type = 'text/plain'

        if file_type == 'application/pdf':
             reader = PdfReader(BytesIO(content))
             # Optimization: Use list accumulation instead of string concatenation
             text_parts = []
             for page in reader.pages:
                 text_parts.append(page.extract_text())
             text = "".join(text_parts)
        else:
            text = content.decode("utf-8")
        
        # Extract topics (Heuristic - no key needed)
        topics = extract_topics(text)

        # Save to storage with topics
        save_study_material(text, file.filename, topics)
        
        return {"text": text, "filename": file.filename, "topics": topics}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

class AnalyzeRequest(BaseModel):
    pass # No fields needed now

@app.post("/analyze-topics")
def analyze_topics_endpoint(request: AnalyzeRequest):
    data = load_study_material()
    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found to analyze")

    text = data.get("text")
    source = data.get("source")
    
    # Heuristic extraction
    topics = extract_topics(text)
    
    # Update storage
    save_study_material(text, source, topics)
    
    return {"topics": topics}

@app.post("/generate-quiz")
def generate_quiz_endpoint(request: QuizRequest):
    data = load_study_material()
    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found. Upload a file first.")
    
    text = data.get("text")
    
    # Priority: Request API Key > Env API Key
    api_key = request.api_key or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
         raise HTTPException(status_code=400, detail="API Key is required for quiz generation.")

    if request.quiz_type == "open-ended":
        questions = generate_open_questions(text, api_key, request.topics)
    else:
        questions = generate_quiz(text, api_key, request.topics)
    
    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate quiz. Please try again.")
        
    return {"questions": questions}

class EvaluationRequest(BaseModel):
    question: str
    user_answer: str
    api_key: Optional[str] = None

@app.post("/evaluate-answer")
def evaluate_answer_endpoint(request: EvaluationRequest):
    data = load_study_material()
    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found.")
        
    text = data.get("text")
    api_key = request.api_key or os.getenv("OPENAI_API_KEY")

    if not api_key:
         raise HTTPException(status_code=400, detail="API Key is required for evaluation.")
         
    result = evaluate_answer(text, request.question, request.user_answer, api_key)
    return result
