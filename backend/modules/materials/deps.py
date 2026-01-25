from fastapi import Depends
from sqlalchemy.orm import Session
import os
from database import get_db
from modules.materials.ai_service import TopicAIService
from modules.materials.deletion import MaterialDeletionPolicy
from modules.materials.document_service import DocumentService
from modules.materials.upsert import MaterialUpserter
from modules.materials.repository import (
    MaterialDeletionRepository,
    MaterialReadRepository,
    MaterialUpsertRepository,
)
from modules.materials.service import MaterialService
from modules.materials.topic_service import TopicService
from modules.quizzes.repository import QuizResultCleanupRepository
from repositories.student_repository import StudentXpRepository
from modules.quizzes.ports import QuizResultCleanupPort
from modules.auth.ports import StudentXpRepositoryPort


def get_material_read_repo(db: Session = Depends(get_db)):
    return MaterialReadRepository(db)


def get_material_upsert_repo(db: Session = Depends(get_db)):
    return MaterialUpsertRepository(db)


def get_material_deletion_repo(db: Session = Depends(get_db)):
    return MaterialDeletionRepository(db)


def get_student_xp_repo(db: Session = Depends(get_db)):
    return StudentXpRepository(db)


def get_quiz_repo(db: Session = Depends(get_db)):
    return QuizResultCleanupRepository(db)


def get_ai_service(api_key: str | None = None):
    key = api_key or os.getenv("OPENAI_API_KEY")
    return TopicAIService(key)


def get_document_service():
    return DocumentService()


def get_topic_service():
    return TopicService()


def get_material_service(
    read_repo: MaterialReadRepository = Depends(get_material_read_repo),
    upsert_repo: MaterialUpsertRepository = Depends(get_material_upsert_repo),
    deletion_repo: MaterialDeletionRepository = Depends(get_material_deletion_repo),
    doc_service: DocumentService = Depends(get_document_service),
    topic_service: TopicService = Depends(get_topic_service),
    student_repo: StudentXpRepositoryPort = Depends(get_student_xp_repo),
    quiz_repo: QuizResultCleanupPort = Depends(get_quiz_repo)
):
    upserter = MaterialUpserter(upsert_repo)
    deletion_policy = MaterialDeletionPolicy(deletion_repo, student_repo, quiz_repo)
    return MaterialService(read_repo, doc_service, topic_service, upserter, deletion_policy)
