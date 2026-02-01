import pytest
from types import SimpleNamespace
from unittest.mock import Mock
from schemas.study import QuizRequest
from modules.quizzes.use_cases import GenerateQuizUseCase
from modules.quizzes.errors import QuizServiceError


def _build_material():
    topic = SimpleNamespace(name="Biologia", concepts=[SimpleNamespace(name="Celula")])
    return SimpleNamespace(id=1, text="conteudo", total_xp=0, topics=[topic])


def _build_use_case():
    material_repo = Mock()
    material_repo.load.return_value = _build_material()

    topic_selector = Mock()
    topic_selector.select.return_value = ([], [])

    strategy_factory = Mock()
    strategy_factory.select_strategy.return_value = object()

    return GenerateQuizUseCase(material_repo, topic_selector, strategy_factory)


def test_generate_quiz_retries_when_llm_missing_concepts():
    use_case = _build_use_case()
    request = QuizRequest(topics=[], quiz_type="short_answer")

    ai_service = Mock()
    ai_service.is_available.return_value = True
    ai_service.generate_quiz.side_effect = [
        [{"question": "Q1?"}],
        [{"question": "Q1?", "concepts": ["Celula"]}],
    ]

    questions = use_case.execute(1, request, ai_service)

    assert len(questions) == 1
    assert ai_service.generate_quiz.call_count == 2


def test_generate_quiz_fails_after_retry_when_llm_missing_concepts():
    use_case = _build_use_case()
    request = QuizRequest(topics=[], quiz_type="short_answer")

    ai_service = Mock()
    ai_service.is_available.return_value = True
    ai_service.generate_quiz.side_effect = [
        [{"question": "Q1?"}],
        [{"question": "Q1?"}],
    ]

    with pytest.raises(QuizServiceError):
        use_case.execute(1, request, ai_service)
