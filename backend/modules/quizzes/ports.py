from typing import Protocol, TYPE_CHECKING, List, Dict, Any

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
        xp_earned: int,
        duration_seconds: int,
        active_seconds: int
    ) -> int: ...


class QuizStrategyFactoryPort(Protocol):
    def select_strategy(self, quiz_type: str, material_xp: int) -> Any:
        ...
    def select_evaluation_strategy(self, quiz_type: str) -> Any:
        ...


class QuizResultPersistencePort(Protocol):
    def record_quiz_result(
        self,
        student_id: int,
        score: int,
        total: int,
        quiz_type: str,
        analytics_data: List[Dict],
        material_id: int | None,
        xp_earned: int,
        duration_seconds: int,
        active_seconds: int
    ) -> int: ...


class LLMServicePort(Protocol):
    def is_available(self) -> bool: ...


class QuizGeneratorPort(LLMServicePort, Protocol):
    def generate_quiz(self, strategy: Any, text: str, topics: List[str] | None = None, priority_topics: List[str] | None = None, material_concepts: List[str] | None = None) -> List[Dict] | None: ...

class AnswerEvaluatorPort(LLMServicePort, Protocol):
    def evaluate_answer(self, strategy: Any, text: str, question: str, user_answer: str) -> Dict: ...

class QuizAIServicePort(QuizGeneratorPort, AnswerEvaluatorPort, Protocol):
    # Composite protocol for backward compatibility or unified services
    pass


class GenerateQuizUseCasePort(Protocol):
    def execute(self, user_id: int, request: "QuizRequest", ai_service: "QuizGeneratorPort") -> List[Dict]: ...


class EvaluateAnswerUseCasePort(Protocol):
    def execute(self, user_id: int, request: "EvaluationRequest", ai_service: "AnswerEvaluatorPort") -> Dict: ...


class SaveQuizResultUseCasePort(Protocol):
    def execute(self, user_id: int, result: "QuizResultCreate") -> None: ...
