import asyncio
from modules.materials.document_service import DocumentService
from modules.materials.deletion import MaterialDeletionPolicy
from modules.materials.mapper import MaterialMapper
from modules.materials.topic_service import TopicService
from modules.materials.upsert import MaterialUpserter
from services.ports import MaterialReaderRepositoryPort, TopicAIServicePort

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit


class MaterialServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class MaterialService:
    def __init__(
        self,
        repo: MaterialReaderRepositoryPort,
        doc_service: DocumentService,
        topic_service: TopicService,
        upserter: MaterialUpserter,
        deletion_policy: MaterialDeletionPolicy
    ):
        self.repo = repo
        self.doc_service = doc_service
        self.topic_service = topic_service
        self.upserter = upserter
        self.deletion_policy = deletion_policy

    async def upload_material(
        self,
        user_id: int,
        file_content: bytes,
        filename: str,
        file_type: str | None,
        ai_service: TopicAIServicePort
    ) -> dict:
        if not ai_service or not ai_service.client:
            raise MaterialServiceError("API Key is required for topic extraction.")

        # Security Check: File Size Limit
        if len(file_content) > MAX_FILE_SIZE:
            raise MaterialServiceError("File too large. Maximum size is 10MB.", status_code=413)

        if not file_type:
            if filename.endswith(".pdf"):
                file_type = "application/pdf"
            else:
                file_type = "text/plain"

        # 1. Extract Text
        text = await asyncio.to_thread(self.doc_service.extract_text, file_content, file_type)
        if not text:
            raise MaterialServiceError("Failed to extract text from file.")

        # 2. Extract Topics (AI)
        topics = await asyncio.to_thread(self.topic_service.extract_topics, text, ai_service)

        # 3. Save
        self.upserter.upsert(user_id, text, filename, topics)

        return {"text": text, "filename": filename, "topics": topics}

    def analyze_topics(self, user_id: int, ai_service: TopicAIServicePort) -> dict:
        if not ai_service or not ai_service.client:
            raise MaterialServiceError("API Key is required for topic extraction.")

        material = self.repo.load(user_id)
        if not material or not material.text:
            raise MaterialServiceError("No material found to analyze")

        text = material.text
        source = material.source

        topics = self.topic_service.extract_topics(text, ai_service)
        self.upserter.upsert(user_id, text, source, topics)

        return {"topics": topics}

    def get_current_material(self, user_id: int) -> dict | None:
        material = self.repo.load(user_id)
        if not material:
            return None
        return MaterialMapper.to_dict(material)

    def clear_material(self, user_id: int) -> bool:
        return self.repo.clear(user_id)

    def list_materials(self, user_id: int) -> list[dict]:
        materials = self.repo.list_all(user_id)
        return [MaterialMapper.to_list_item(material) for material in materials]

    def activate_material(self, user_id: int, material_id: int) -> bool:
        return self.repo.activate(user_id, material_id)

    def delete_material(self, user_id: int, material_id: int) -> bool:
        return self.deletion_policy.delete(user_id, material_id)
