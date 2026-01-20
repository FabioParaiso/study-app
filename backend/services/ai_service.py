from openai import OpenAI
import json
from .quiz_strategies import QuizGenerationStrategy
from .topic_extractor import TopicExtractor
from .answer_evaluator import AnswerEvaluator

class AIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_quiz(self, strategy: QuizGenerationStrategy, text: str, topics: list[str] = None, priority_topics: list[str] = None) -> list[dict]:
        if not self.client: return None
        
        prompt = strategy.generate_prompt(text, topics, priority_topics)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a JSON generator. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            content = response.choices[0].message.content
            return strategy.parse_response(content)
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None

    def evaluate_answer(self, text: str, question: str, user_answer: str) -> dict:
        if not self.client: return None

        prompt = AnswerEvaluator.generate_prompt(text, question, user_answer)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a teacher grading a test. Return JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return {"score": 0, "feedback": "Erro ao avaliar. Tenta novamente."}

    def extract_topics(self, text: str, existing_topics: list[str]) -> list[str]:
        if not self.client: return ["Tópicos Gerais"]

        prompt = TopicExtractor.generate_prompt(text, existing_topics)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a JSON generator. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            return TopicExtractor.parse_response(data)
        except Exception as e:
            print(f"Error extracting topics: {e}")
            return ["Tópicos Gerais"]
