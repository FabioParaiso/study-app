from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from logic import extract_text_from_file, generate_quiz, extract_topics
from storage import save_study_material, load_study_material, clear_study_material
from io import BytesIO
from pypdf import PdfReader
import json

load_dotenv()

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
async def upload_file(file: UploadFile = File(...), api_key: Optional[str] = Form(None)):
    try:
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
             # ⚡ Bolt Optimization: Use list join instead of string concatenation
             pages_text = []
             for page in reader.pages:
                 pages_text.append(page.extract_text())
             text = "".join(pages_text)
        else:
            text = content.decode("utf-8")
        
        # Extract topics
        # Prioritize key passed in form, then env
        key_to_use = api_key or os.getenv("OPENAI_API_KEY") 
        topics = []
        if key_to_use:
             topics = extract_topics(text, key_to_use)

        # Save to storage with topics
        save_study_material(text, file.filename, topics)
        
        return {"text": text, "filename": file.filename, "topics": topics}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AnalyzeRequest(BaseModel):
    api_key: Optional[str] = None

@app.post("/analyze-topics")
def analyze_topics_endpoint(request: AnalyzeRequest):
    data = load_study_material()
    if not data or not data.get("text"):
        raise HTTPException(status_code=400, detail="No material found to analyze")

    text = data.get("text")
    source = data.get("source")
    
    key_to_use = request.api_key or os.getenv("OPENAI_API_KEY")
    if not key_to_use:
        raise HTTPException(status_code=400, detail="API Key required to analyze topics")

    topics = extract_topics(text, key_to_use)
    
    # Update storage
    save_study_material(text, source, topics)
    
    return {"topics": topics}

@app.post("/generate-quiz")
def generate_quiz_endpoint(request: QuizRequest):
    api_key = request.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="API Key required")
    
    text_to_use = request.text
    
    if request.use_saved:
        saved = load_study_material()
        if saved:
            text_to_use = saved.get("text")
    
    if not text_to_use:
         raise HTTPException(status_code=400, detail="No text provided and no saved material found.")

    # Call logic.py's generate_quiz
    quiz = generate_quiz(text_to_use, api_key, request.topics)
    if not quiz:
        raise HTTPException(status_code=500, detail="Failed to generate quiz")
    
    return quiz
