import asyncio
from modules.materials.errors import MAX_FILE_SIZE, MaterialServiceError
from modules.materials.file_types import FileTypeResolver
from modules.materials.mapper import MaterialMapper
from modules.materials.ports import (
    AnalyzeTopicsUseCasePort,
    ActivateMaterialUseCasePort,
    ClearMaterialUseCasePort,
    DeleteMaterialUseCasePort,
    DocumentServicePort,
    FileTypeResolverPort,
    GetCurrentMaterialUseCasePort,
    ListMaterialsUseCasePort,
    MaterialDeletionTransactionPort,
    MaterialReaderRepositoryPort,
    MaterialUpserterPort,
    TopicAIServicePort,
    TopicServicePort,
    UploadMaterialUseCasePort,
)


class UploadMaterialUseCase(UploadMaterialUseCasePort):
    def __init__(
        self,
        doc_service: DocumentServicePort,
        topic_service: TopicServicePort,
        upserter: MaterialUpserterPort,
        file_type_resolver: FileTypeResolverPort | None = None
    ):
        self.doc_service = doc_service
        self.topic_service = topic_service
        self.upserter = upserter
        self.file_type_resolver = file_type_resolver or FileTypeResolver()

    async def execute(
        self,
        user_id: int,
        file_content: bytes,
        filename: str,
        file_type: str | None,
        ai_service: TopicAIServicePort
    ) -> dict:
        if len(file_content) > MAX_FILE_SIZE:
            raise MaterialServiceError("File too large. Maximum size is 10MB.", status_code=413)

        if not ai_service or not ai_service.is_available():
            raise MaterialServiceError("API Key is required for topic extraction.")

        resolved_type = self.file_type_resolver.resolve(filename, file_type)

        text = await asyncio.to_thread(self.doc_service.extract_text, file_content, resolved_type)
        if not text:
            raise MaterialServiceError("Failed to extract text from file.")

        topics = await asyncio.to_thread(self.topic_service.extract_topics, text, ai_service)
        self.upserter.upsert(user_id, text, filename, topics)

        return {"text": text, "filename": filename, "topics": topics}


class AnalyzeTopicsUseCase(AnalyzeTopicsUseCasePort):
    def __init__(self, repo: MaterialReaderRepositoryPort, topic_service: TopicServicePort, upserter: MaterialUpserterPort):
        self.repo = repo
        self.topic_service = topic_service
        self.upserter = upserter

    def execute(self, user_id: int, ai_service: TopicAIServicePort) -> dict:
        if not ai_service or not ai_service.is_available():
            raise MaterialServiceError("API Key is required for topic extraction.")

        material = self.repo.load(user_id)
        if not material or not material.text:
            raise MaterialServiceError("No material found to analyze")

        topics = self.topic_service.extract_topics(material.text, ai_service)
        self.upserter.upsert(user_id, material.text, material.source, topics)

        return {"topics": topics}


class GetCurrentMaterialUseCase(GetCurrentMaterialUseCasePort):
    def __init__(self, repo: MaterialReaderRepositoryPort):
        self.repo = repo

    def execute(self, user_id: int) -> dict | None:
        material = self.repo.load(user_id)
        if not material:
            return None
        return MaterialMapper.to_dict(material)


class ClearMaterialUseCase(ClearMaterialUseCasePort):
    def __init__(self, repo: MaterialReaderRepositoryPort):
        self.repo = repo

    def execute(self, user_id: int) -> bool:
        return self.repo.clear(user_id)


class ListMaterialsUseCase(ListMaterialsUseCasePort):
    def __init__(self, repo: MaterialReaderRepositoryPort):
        self.repo = repo

    def execute(self, user_id: int) -> list[dict]:
        materials = self.repo.list_all(user_id)
        return [MaterialMapper.to_list_item(material) for material in materials]


class ActivateMaterialUseCase(ActivateMaterialUseCasePort):
    def __init__(self, repo: MaterialReaderRepositoryPort):
        self.repo = repo

    def execute(self, user_id: int, material_id: int) -> bool:
        return self.repo.activate(user_id, material_id)


class DeleteMaterialUseCase(DeleteMaterialUseCasePort):
    def __init__(self, deletion_policy: MaterialDeletionTransactionPort):
        self.deletion_policy = deletion_policy

    def execute(self, user_id: int, material_id: int) -> bool:
        return self.deletion_policy.delete_with_cleanup(user_id, material_id)
