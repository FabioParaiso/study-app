from unittest.mock import patch
from modules.quizzes.policies import QuestionPostProcessor, QuizStrategyFactory
from modules.quizzes.registry import build_default_quiz_registry
from modules.quizzes.engine import MultipleChoiceStrategy, OpenEndedStrategy


def test_question_post_processor_updates_correct_index():
    questions = [
        {"options": ["A", "B", "C"], "correctIndex": 0}
    ]

    def reverse_list(items):
        items.reverse()

    with patch("modules.quizzes.policies.random.shuffle", side_effect=reverse_list):
        processed = QuestionPostProcessor("multiple-choice").apply(questions)

    assert processed[0]["options"] == ["C", "B", "A"]
    assert processed[0]["correctIndex"] == 2


def test_quiz_strategy_factory_open_ended_not_blocked_by_xp():
    factory = QuizStrategyFactory(build_default_quiz_registry())

    strategy = factory.select_strategy("open-ended", material_xp=0)

    assert isinstance(strategy, OpenEndedStrategy)


def test_quiz_strategy_factory_defaults_to_multiple_choice():
    factory = QuizStrategyFactory(build_default_quiz_registry())

    strategy = factory.select_strategy("unknown-type", material_xp=0)

    assert isinstance(strategy, MultipleChoiceStrategy)
