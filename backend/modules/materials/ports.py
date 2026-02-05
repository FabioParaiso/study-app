from typing import Protocol, TYPE_CHECKING, Dict, List, Tuple, Any

if TYPE_CHECKING:
    from models import StudyMaterial


class MaterialUpsertRepositoryPort(Protocol):
    def deactivate_all(self, student_id: int, commit: bool = True) -> bool: ...
    def find_by_source(self, student_id: int, source_name: str) -> Any: ...
    def save_material(self, material: Any) -> Any: ...


class MaterialLoaderPort(Protocol):
    def load(self, student_id: int) -> Any: ...


class MaterialReaderRepositoryPort(Protocol):
    def load(self, student_id: int) -> Any: ...
    def list_all(self, student_id: int) -> List["StudyMaterial"]: ...
    def activate(self, student_id: int, material_id: int) -> bool: ...
    def clear(self, student_id: int) -> bool: ...


class MaterialConceptIdRepositoryPort(Protocol):
    def get_concept_id_map(self, material_id: int) -> Dict[str, int]: ...
    def get_concept_pair_id_map(self, material_id: int) -> Dict[Tuple[str, str], int]: ...


class MaterialConceptPairsRepositoryPort(Protocol):
    def get_concept_pairs(self, material_id: int) -> List[Tuple[str, str]]: ...
    def get_concept_pairs_for_student(self, student_id: int) -> List[Tuple[str, str]]: ...


class DocumentServicePort(Protocol):
    def extract_text(self, file_content: bytes, file_type: str) -> str | None: ...


class FileTypeResolverPort(Protocol):
    def resolve(self, filename: str, explicit_type: str | None) -> str: ...


class MaterialUpserterPort(Protocol):
    def upsert(self, student_id: int, text: str, source_name: str, topics: Dict[str, List[str]] | None) -> Any: ...


class MaterialDeletionTransactionPort(Protocol):
    def delete_with_cleanup(self, user_id: int, material_id: int) -> bool: ...


class TopicAIServicePort(Protocol):
    def is_available(self) -> bool: ...
    def extract_topics(self, text: str) -> Dict[str, List[str]]: ...


class TopicServicePort(Protocol):
    def extract_topics(self, text: str, ai_service: "TopicAIServicePort") -> Dict[str, List[str]]: ...


class UploadMaterialUseCasePort(Protocol):
    async def execute(
        self,
        user_id: int,
        file_content: bytes,
        filename: str,
        file_type: str | None,
        ai_service: "TopicAIServicePort"
    ) -> Dict: ...


class AnalyzeTopicsUseCasePort(Protocol):
    def execute(self, user_id: int, ai_service: "TopicAIServicePort") -> Dict: ...


class GetCurrentMaterialUseCasePort(Protocol):
    def execute(self, user_id: int) -> Dict | None: ...


class ClearMaterialUseCasePort(Protocol):
    def execute(self, user_id: int) -> bool: ...


class ListMaterialsUseCasePort(Protocol):
    def execute(self, user_id: int) -> List[Dict]: ...


class ActivateMaterialUseCasePort(Protocol):
    def execute(self, user_id: int, material_id: int) -> bool: ...


class DeleteMaterialUseCasePort(Protocol):
    def execute(self, user_id: int, material_id: int) -> bool: ...


class TopicSelectorPort(Protocol):
    def select(
        self,
        user_id: int,
        material_id: int | None,
        requested_topics: List[str] | None
    ) -> Tuple[List[str], List[str]]: ...
