import json
from typing import Any
from modules.common.ports import LLMCallerPort
from modules.quizzes.engine import QuizGenerationStrategy
from modules.quizzes.answer_evaluator import AnswerEvaluator


class QuizAIService:
    MODEL_QUIZ_GENERATION = "gpt-4o-mini"
    MODEL_ANSWER_EVALUATION = "gpt-4o-mini"

    def __init__(self, caller: LLMCallerPort | None):
        self.caller = caller

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
            model=self.MODEL_QUIZ_GENERATION
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
            model=self.MODEL_ANSWER_EVALUATION
        )

        if content is None:
            return {"score": 0, "feedback": "Erro ao avaliar. Tenta novamente."}

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"score": 0, "feedback": "Erro ao processar avaliação."}
