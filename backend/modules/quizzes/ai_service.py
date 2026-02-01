import json
from typing import Any
from llm_models import get_llm_models
from modules.common.ports import LLMCallerPort
from modules.quizzes.engine import QuizGenerationStrategy
from modules.quizzes.answer_evaluator import AnswerEvaluator


class QuizAIService:

    def __init__(self, caller: LLMCallerPort | None):
        self.caller = caller
        models = get_llm_models()
        self.model_quiz_generation = models.quiz_generation
        self.model_answer_evaluation = models.answer_evaluation
        self.reasoning_effort = models.reasoning_effort

    def is_available(self) -> bool:
        return bool(self.caller and self.caller.is_available())

    def generate_quiz(
        self,
        strategy: QuizGenerationStrategy,
        text: str,
        topics: list[str] | None = None,
        priority_topics: list[str] | None = None,
        material_concepts: list[str] | None = None
    ) -> list[dict] | None:
        if not self.is_available():
            return None
        prompt = strategy.generate_prompt(text, topics, priority_topics, material_concepts)

        content = self.caller.call(
            prompt=prompt,
            system_message="És um gerador de JSON. Devolve apenas JSON válido.",
            model=self.model_quiz_generation,
            reasoning_effort=self.reasoning_effort
        )

        if content is None:
            return None
        return strategy.parse_response(content)

    def evaluate_answer(self, strategy: Any, text: str, question: str, user_answer: str) -> dict:
        if not self.is_available():
            return {"score": 0, "feedback": "Erro ao avaliar. Tenta novamente."}
        prompt = AnswerEvaluator.generate_prompt(strategy, text, question, user_answer)

        content = self.caller.call(
            prompt=prompt,
            system_message="És um professor a corrigir um teste. Devolve JSON.",
            model=self.model_answer_evaluation,
            reasoning_effort=self.reasoning_effort
        )

        if content is None:
            return {"score": 0, "feedback": "Erro ao avaliar. Tenta novamente."}

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"score": 0, "feedback": "Erro ao processar avaliação."}
