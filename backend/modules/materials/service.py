import asyncio
from fastapi import UploadFile
from modules.materials.document_service import DocumentService
from modules.materials.deletion import MaterialDeletionPolicy
from modules.materials.topic_service import TopicService
from modules.materials.upsert import MaterialUpserter
from services.ports import MaterialRepositoryPort, StudentRepositoryPort, TopicAIServicePort

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit


class MaterialServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class MaterialService:
    def __init__(
        self,
        repo: MaterialRepositoryPort,
        doc_service: DocumentService,
        topic_service: TopicService,
        student_repo: StudentRepositoryPort,
        upserter: MaterialUpserter | None = None,
        deletion_policy: MaterialDeletionPolicy | None = None
    ):
        self.repo = repo
        self.doc_service = doc_service
        self.topic_service = topic_service
        self.student_repo = student_repo
        self.upserter = upserter or MaterialUpserter(repo)
        self.deletion_policy = deletion_policy or MaterialDeletionPolicy(repo, student_repo)

    async def upload_material(self, user_id: int, file: UploadFile, ai_service: TopicAIServicePort) -> dict:
        if not ai_service or not ai_service.client:
            raise MaterialServiceError("API Key is required for topic extraction.")

        # Security Check: File Size Limit
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            raise MaterialServiceError("File too large. Maximum size is 10MB.", status_code=413)

        content = await file.read()
        file_type = file.content_type

        if not file_type:
            if file.filename.endswith(".pdf"):
                file_type = "application/pdf"
            else:
                file_type = "text/plain"

        # 1. Extract Text
        text = await asyncio.to_thread(self.doc_service.extract_text, content, file_type)
        if not text:
            raise MaterialServiceError("Failed to extract text from file.")

        # 2. Extract Topics (AI)
        topics = await asyncio.to_thread(self.topic_service.extract_topics, text, ai_service)

        # 3. Save
        self.upserter.upsert(user_id, text, file.filename, topics)

        return {"text": text, "filename": file.filename, "topics": topics}

    def analyze_topics(self, user_id: int, ai_service: TopicAIServicePort) -> dict:
        if not ai_service or not ai_service.client:
            raise MaterialServiceError("API Key is required for topic extraction.")

        data = self.repo.load(user_id)
        if not data or not data.get("text"):
            raise MaterialServiceError("No material found to analyze")

        text = data.get("text")
        source = data.get("source")

        topics = self.topic_service.extract_topics(text, ai_service)
        self.upserter.upsert(user_id, text, source, topics)

        return {"topics": topics}

    def get_current_material(self, user_id: int) -> dict | None:
        return self.repo.load(user_id)

    def clear_material(self, user_id: int) -> bool:
        return self.repo.clear(user_id)

    def list_materials(self, user_id: int) -> list[dict]:
        return self.repo.list_all(user_id)

    def activate_material(self, user_id: int, material_id: int) -> bool:
        return self.repo.activate(user_id, material_id)

    def delete_material(self, user_id: int, material_id: int) -> bool:
        return self.deletion_policy.delete(user_id, material_id)
