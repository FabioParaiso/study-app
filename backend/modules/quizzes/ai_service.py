import json
from modules.quizzes.engine import QuizGenerationStrategy, ShortAnswerStrategy, OpenEndedStrategy
from modules.quizzes.answer_evaluator import AnswerEvaluator
from services.openai_client import OpenAIClientAdapter
from services.openai_caller import OpenAICaller
from modules.common.ports import OpenAIClientPort


class QuizAIService:
    MODEL_QUIZ_GENERATION = "gpt-4o-mini"
    MODEL_ANSWER_EVALUATION = "gpt-4o-mini"

    def __init__(self, api_key: str, client: OpenAIClientPort | None = None, caller: OpenAICaller | None = None):
        if caller:
            self.client = caller.client
            self.caller = caller
        else:
            if client:
                self.client = client
            elif api_key:
                self.client = OpenAIClientAdapter(api_key=api_key)
            else:
                self.client = None
            self.caller = OpenAICaller(self.client)

    def generate_quiz(
        self,
        strategy: QuizGenerationStrategy,
        text: str,
        topics: list[str] | None = None,
        priority_topics: list[str] | None = None,
        material_concepts: list[str] | None = None
    ) -> list[dict] | None:
        prompt = strategy.generate_prompt(text, topics, priority_topics, material_concepts)

        content = self.caller.call(
            prompt=prompt,
            system_message="You are a JSON generator. Output only valid JSON.",
            model=self.MODEL_QUIZ_GENERATION
        )

        if content is None:
            return None
        return strategy.parse_response(content)

    def evaluate_answer(self, text: str, question: str, user_answer: str, quiz_type: str = "open-ended") -> dict:
        strategy = ShortAnswerStrategy() if quiz_type == "short_answer" else OpenEndedStrategy()
        prompt = AnswerEvaluator.generate_prompt(strategy, text, question, user_answer)

        content = self.caller.call(
            prompt=prompt,
            system_message="You are a teacher grading a test. Return JSON.",
            model=self.MODEL_ANSWER_EVALUATION
        )

        if content is None:
            return {"score": 0, "feedback": "Erro ao avaliar. Tenta novamente."}

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"score": 0, "feedback": "Erro ao processar avaliação."}
