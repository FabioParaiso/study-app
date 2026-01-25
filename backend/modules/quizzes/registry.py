from dataclasses import dataclass
from typing import Callable
from modules.quizzes.engine import (
    QuizGenerationStrategy,
    EvaluationStrategy,
    MultipleChoiceStrategy,
    OpenEndedStrategy,
    ShortAnswerStrategy,
    MultipleChoiceEvaluationStrategy,
    OpenEndedEvaluationStrategy,
    ShortAnswerEvaluationStrategy,
)


@dataclass(frozen=True)
class QuizTypeDefinition:
    min_xp: int
    strategy_factory: Callable[[], QuizGenerationStrategy]
    evaluation_factory: Callable[[], EvaluationStrategy]


class QuizTypeRegistry:
    def __init__(self, default_generation_type: str, default_evaluation_type: str):
        self._registry: dict[str, QuizTypeDefinition] = {}
        self._default_generation_type = default_generation_type
        self._default_evaluation_type = default_evaluation_type

    def register(self, quiz_type: str, definition: QuizTypeDefinition) -> None:
        self._registry[quiz_type] = definition

    def get_for_generation(self, quiz_type: str) -> QuizTypeDefinition:
        return self._registry.get(quiz_type) or self._registry[self._default_generation_type]

    def get_for_evaluation(self, quiz_type: str) -> QuizTypeDefinition:
        return self._registry.get(quiz_type) or self._registry[self._default_evaluation_type]


def build_default_quiz_registry() -> QuizTypeRegistry:
    registry = QuizTypeRegistry(
        default_generation_type="multiple-choice",
        default_evaluation_type="open-ended"
    )
    registry.register(
        "open-ended",
        QuizTypeDefinition(
            min_xp=900,
            strategy_factory=OpenEndedStrategy,
            evaluation_factory=OpenEndedEvaluationStrategy
        ),
    )
    registry.register(
        "short_answer",
        QuizTypeDefinition(
            min_xp=300,
            strategy_factory=ShortAnswerStrategy,
            evaluation_factory=ShortAnswerEvaluationStrategy
        ),
    )
    registry.register(
        "multiple-choice",
        QuizTypeDefinition(
            min_xp=0,
            strategy_factory=MultipleChoiceStrategy,
            evaluation_factory=MultipleChoiceEvaluationStrategy
        ),
    )
    registry.register(
        "multiple",
        QuizTypeDefinition(
            min_xp=0,
            strategy_factory=MultipleChoiceStrategy,
            evaluation_factory=MultipleChoiceEvaluationStrategy
        ),
    )
    return registry
