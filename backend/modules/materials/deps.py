from fastapi import Depends
from sqlalchemy.orm import Session
import os
from database import get_db
from modules.materials.ai_service import TopicAIService
from modules.materials.document_service import DocumentService
from modules.materials.repository import MaterialRepository
from modules.materials.service import MaterialService
from modules.materials.topic_service import TopicService
from modules.quizzes.repository import QuizRepository
from repositories.student_repository import StudentRepository


def get_material_repo(db: Session = Depends(get_db)):
    return MaterialRepository(db)


def get_student_repo(db: Session = Depends(get_db)):
    return StudentRepository(db)


def get_quiz_repo(db: Session = Depends(get_db)):
    return QuizRepository(db)


def get_ai_service(api_key: str | None = None):
    key = api_key or os.getenv("OPENAI_API_KEY")
    return TopicAIService(key)


def get_document_service():
    return DocumentService()


def get_topic_service():
    return TopicService()


def get_material_service(
    repo: MaterialRepository = Depends(get_material_repo),
    doc_service: DocumentService = Depends(get_document_service),
    topic_service: TopicService = Depends(get_topic_service),
    student_repo: StudentRepository = Depends(get_student_repo),
    quiz_repo: QuizRepository = Depends(get_quiz_repo)
):
    return MaterialService(repo, doc_service, topic_service, student_repo, quiz_repo)
