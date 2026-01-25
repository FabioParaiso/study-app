from typing import Protocol, TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    from schemas.study import EvaluationRequest, QuizRequest, QuizResultCreate


class QuizResultRecorderPort(Protocol):
    def record(
        self,
        user_id: int,
        score: int,
        total_questions: int,
        quiz_type: str,
        analytics_data: List[Dict],
        material_id: int | None,
        xp_earned: int
    ) -> None: ...


class QuizStrategyFactoryPort(Protocol):
    def select_strategy(self, quiz_type: str, material_xp: int) -> Any:
        ...


class QuizResultWriterPort(Protocol):
    def save_quiz_result(self, student_id: int, score: int, total: int, quiz_type: str, analytics_data: List[Dict], material_id: int | None = None) -> bool: ...


class QuizResultCleanupPort(Protocol):
    def delete_results_for_material(self, material_id: int) -> int: ...


class QuizAIServicePort(Protocol):
    client: Any | None
    def generate_quiz(self, strategy: Any, text: str, topics: List[str] | None = None, priority_topics: List[str] | None = None, material_concepts: List[str] | None = None) -> List[Dict] | None: ...
    def evaluate_answer(self, text: str, question: str, user_answer: str, quiz_type: str = "open-ended") -> Dict: ...


class QuizServicePort(Protocol):
    def generate_quiz(self, user_id: int, request: "QuizRequest", ai_service: "QuizAIServicePort") -> List[Dict]: ...
    def evaluate_answer(self, user_id: int, request: "EvaluationRequest", ai_service: "QuizAIServicePort") -> Dict: ...
    def save_quiz_result(self, user_id: int, result: "QuizResultCreate") -> None: ...
