from fastapi import Depends
from sqlalchemy.orm import Session
import os
from database import get_db
from modules.materials.ai_service import TopicAIService
from modules.materials.deletion import MaterialDeletionTransaction
from modules.materials.document_registry import DocumentTypeRegistry
from modules.materials.document_service import DocumentService, PdfTextExtractor, PlainTextExtractor
from modules.materials.file_types import FileTypeResolver
from modules.materials.upsert import MaterialUpserter
from modules.materials.repository import (
    MaterialReadRepository,
    MaterialUpsertRepository,
)
from modules.materials.topic_service import TopicService
from modules.materials.use_cases import (
    UploadMaterialUseCase,
    AnalyzeTopicsUseCase,
    GetCurrentMaterialUseCase,
    ClearMaterialUseCase,
    ListMaterialsUseCase,
    ActivateMaterialUseCase,
    DeleteMaterialUseCase,
)
from services.llm_provider import build_openai_caller


def get_material_read_repo(db: Session = Depends(get_db)):
    return MaterialReadRepository(db)


def get_material_upsert_repo(db: Session = Depends(get_db)):
    return MaterialUpsertRepository(db)


def get_ai_service(api_key: str | None = None):
    key = api_key or os.getenv("OPENAI_API_KEY")
    caller = build_openai_caller(key)
    return TopicAIService(caller)


def get_document_registry():
    return DocumentTypeRegistry(
        {
            "application/pdf": PdfTextExtractor(),
            "text/plain": PlainTextExtractor(),
        }
    )


def get_document_service(registry: DocumentTypeRegistry = Depends(get_document_registry)):
    return DocumentService(registry)


def get_topic_service():
    return TopicService()


def get_file_type_resolver():
    return FileTypeResolver()


def get_upload_material_use_case(
    upsert_repo: MaterialUpsertRepository = Depends(get_material_upsert_repo),
    doc_service: DocumentService = Depends(get_document_service),
    topic_service: TopicService = Depends(get_topic_service),
    file_type_resolver: FileTypeResolver = Depends(get_file_type_resolver),
):
    upserter = MaterialUpserter(upsert_repo)
    return UploadMaterialUseCase(doc_service, topic_service, upserter, file_type_resolver)


def get_analyze_topics_use_case(
    read_repo: MaterialReadRepository = Depends(get_material_read_repo),
    upsert_repo: MaterialUpsertRepository = Depends(get_material_upsert_repo),
    topic_service: TopicService = Depends(get_topic_service),
):
    upserter = MaterialUpserter(upsert_repo)
    return AnalyzeTopicsUseCase(read_repo, topic_service, upserter)


def get_get_current_material_use_case(
    read_repo: MaterialReadRepository = Depends(get_material_read_repo),
):
    return GetCurrentMaterialUseCase(read_repo)


def get_clear_material_use_case(
    read_repo: MaterialReadRepository = Depends(get_material_read_repo),
):
    return ClearMaterialUseCase(read_repo)


def get_list_materials_use_case(
    read_repo: MaterialReadRepository = Depends(get_material_read_repo),
):
    return ListMaterialsUseCase(read_repo)


def get_activate_material_use_case(
    read_repo: MaterialReadRepository = Depends(get_material_read_repo),
):
    return ActivateMaterialUseCase(read_repo)


def get_delete_material_use_case(
    db: Session = Depends(get_db),
):
    deletion = MaterialDeletionTransaction(db)
    return DeleteMaterialUseCase(deletion)
