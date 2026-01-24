from openai import OpenAI
import json
from .quiz_strategies import QuizGenerationStrategy, ShortAnswerStrategy, OpenEndedStrategy
from .topic_extractor import TopicExtractor
from .answer_evaluator import AnswerEvaluator

class AIService:
    """
    Serviço central para interações com a API OpenAI.
    Gere geração de quizzes, avaliação de respostas e extração de tópicos.
    """
    
    # Modelos configuráveis por tipo de tarefa (facilita mudanças futuras)
    MODEL_QUIZ_GENERATION = "gpt-4o-mini"      # Pode ser upgradeado para gpt-4o
    MODEL_ANSWER_EVALUATION = "gpt-4o-mini"   # Pode ser upgradeado para gpt-4o
    MODEL_TOPIC_EXTRACTION = "gpt-4o-mini"         # Modelo forte e estável para extração
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _call_openai(self, prompt: str, system_message: str, model: str, temperature: float = 0.7, seed: int = None, reasoning_effort: str | None = None) -> str | None:
        """
        Método privado para chamadas à API OpenAI.
        Retorna o conteúdo da resposta ou None em caso de erro.
        """
        if not self.client:
            return None

        if model.startswith("gpt-5"):
            try:
                messages = [{"role": "user", "content": prompt}]
                if system_message:
                    messages.insert(0, {"role": "system", "content": system_message})

                effort = reasoning_effort or "none"
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "reasoning_effort": effort,
                }
                if effort == "none" and temperature is not None:
                    kwargs["temperature"] = temperature
                if seed is not None:
                    kwargs["seed"] = seed

                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI API Error (gpt-5 chat): {e}")
                return None
        try:
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": temperature
            }
            if seed is not None:
                kwargs["seed"] = seed

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return None

    def generate_quiz(self, strategy: QuizGenerationStrategy, text: str, topics: list[str] = None, priority_topics: list[str] = None, material_topics: list[str] = None) -> list[dict]:
        prompt = strategy.generate_prompt(text, topics, priority_topics, material_topics)
        
        content = self._call_openai(
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

        content = self._call_openai(
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

    def extract_topics(self, text: str) -> dict[str, list[str]]:
        # Single call: Extract topics + concepts map
        prompt_topics = TopicExtractor.generate_prompt(text, [])
        
        content_topics = self._call_openai(
            prompt=prompt_topics,
            system_message="You are a JSON generator. Output only valid JSON.",
            model=self.MODEL_TOPIC_EXTRACTION,
            temperature=0.0,
            seed=42,
            reasoning_effort="none"
        )
        
        if content_topics is None:
            return {"Tópicos Gerais": []}
            
        try:
            data_topics = json.loads(content_topics)
            topics_list = TopicExtractor.parse_topics(data_topics)
        except json.JSONDecodeError:
            return {"Tópicos Gerais": []}

        if not topics_list:
            return {"Tópicos Gerais": []}

        try:
            concepts_map = TopicExtractor.parse_concepts(data_topics)
            if not isinstance(concepts_map, dict):
                concepts_map = {}

            # Ensure all extracted topics are present (even if empty)
            final_map = {}
            for t in topics_list:
                concepts = concepts_map.get(t, [])
                final_map[t] = concepts if isinstance(concepts, list) else []
            return final_map
        except Exception:
            return {t: [] for t in topics_list}
