from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from models import StudyMaterial


class MaterialUpsertRepositoryPort(Protocol):
    def deactivate_all(self, student_id: int, commit: bool = True) -> bool: ...
    def find_by_source(self, student_id: int, source_name: str): ...
    def save_material(self, material): ...


class MaterialLoaderPort(Protocol):
    def load(self, student_id: int): ...


class MaterialReaderRepositoryPort(Protocol):
    def load(self, student_id: int): ...
    def list_all(self, student_id: int) -> list["StudyMaterial"]: ...
    def activate(self, student_id: int, material_id: int) -> bool: ...
    def clear(self, student_id: int) -> bool: ...


class MaterialDeletionRepositoryPort(Protocol):
    def get_stats(self, student_id: int, material_id: int) -> dict | None: ...
    def delete(self, student_id: int, material_id: int) -> bool: ...


class MaterialStatsRepositoryPort(Protocol):
    def get_stats_by_id(self, material_id: int) -> dict | None: ...
    def set_stats(self, material_id: int, total_questions_answered: int, correct_answers_count: int, total_xp: int, high_score: int) -> bool: ...


class MaterialConceptIdRepositoryPort(Protocol):
    def get_concept_id_map(self, material_id: int) -> dict[str, int]: ...


class MaterialConceptPairsRepositoryPort(Protocol):
    def get_concept_pairs(self, material_id: int) -> list[tuple[str, str]]: ...
    def get_concept_pairs_for_student(self, student_id: int) -> list[tuple[str, str]]: ...


class DocumentServicePort(Protocol):
    def extract_text(self, file_content: bytes, file_type: str) -> str: ...


class MaterialUpserterPort(Protocol):
    def upsert(self, student_id: int, text: str, source_name: str, topics: dict[str, list[str]] | None): ...


class MaterialDeletionPolicyPort(Protocol):
    def delete(self, user_id: int, material_id: int) -> bool: ...


class TopicSelectorPort(Protocol):
    def select(
        self,
        user_id: int,
        material_id: int | None,
        requested_topics: list[str] | None
    ) -> tuple[list[str], list[str]]: ...


class QuizResultRecorderPort(Protocol):
    def record(
        self,
        user_id: int,
        score: int,
        total_questions: int,
        quiz_type: str,
        analytics_data: list[dict],
        material_id: int | None,
        xp_earned: int
    ) -> None: ...


class QuizResultWriterPort(Protocol):
    def save_quiz_result(self, student_id: int, score: int, total: int, quiz_type: str, analytics_data: list[dict], material_id: int | None = None) -> bool: ...


class QuizResultCleanupPort(Protocol):
    def delete_results_for_material(self, material_id: int) -> int: ...


class StudentAuthRepositoryPort(Protocol):
    def create_student(self, name: str, hashed_password: str): ...
    def get_by_name(self, name: str): ...


class StudentLookupRepositoryPort(Protocol):
    def get_student(self, student_id: int): ...


class StudentXpRepositoryPort(Protocol):
    def get_student(self, student_id: int): ...
    def update_xp(self, student_id: int, amount: int): ...


class StudentGamificationRepositoryPort(Protocol):
    def update_xp(self, student_id: int, amount: int): ...
    def update_avatar(self, student_id: int, avatar: str): ...
    def update_high_score(self, student_id: int, score: int): ...


class QuizAIServicePort(Protocol):
    client: object | None
    def generate_quiz(self, strategy, text: str, topics: list[str] | None = None, priority_topics: list[str] | None = None, material_concepts: list[str] | None = None) -> list[dict] | None: ...
    def evaluate_answer(self, text: str, question: str, user_answer: str, quiz_type: str = "open-ended") -> dict: ...


class TopicAIServicePort(Protocol):
    client: object | None
    def extract_topics(self, text: str) -> dict[str, list[str]]: ...


class TopicServicePort(Protocol):
    def extract_topics(self, text: str, ai_service: "TopicAIServicePort") -> dict[str, list[str]]: ...


class TokenServicePort(Protocol):
    def create_access_token(self, data: dict) -> str: ...
    def decode_access_token(self, token: str) -> dict | None: ...


class AnalyticsRepositoryPort(Protocol):
    def fetch_question_analytics(self, student_id: int, material_id: int | None = None) -> list[dict]: ...


class OpenAIClientPort(Protocol):
    def chat_completions_create(self, **kwargs): ...
