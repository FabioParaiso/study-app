from abc import ABC, abstractmethod
import json


from prompts import quizzes as quiz_prompts

class QuizGenerationStrategy(ABC):
    """
    Classe base abstrata para estratégias de geração de quizzes.
    Contém métodos auxiliares partilhados para construir instruções dinâmicas.
    """
    # Helper methods removed in favor of centralized prompt module

    @abstractmethod
    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        pass

    def parse_response(self, response_content: str) -> list[dict]:
        """Implementação padrão de parsing JSON."""
        try:
            data = json.loads(response_content)
            return data.get("questions", [])
        except json.JSONDecodeError:
            return []


class MultipleChoiceStrategy(QuizGenerationStrategy):
    """
    Modo Iniciante: Perguntas de escolha múltipla.
    Foco na compreensão de conceitos com feedback explicativo.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        return quiz_prompts.get_multiple_choice_prompt(text, topics, priority_topics, material_topics)


class OpenEndedStrategy(QuizGenerationStrategy):
    """
    Modo Avançado: Perguntas de resposta aberta.
    Exige pensamento crítico seguindo a Taxonomia de Bloom.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        return quiz_prompts.get_open_ended_prompt(text, topics, priority_topics, material_topics)

    def generate_evaluation_prompt(self, text: str, question: str, user_answer: str) -> str:
        return quiz_prompts.get_evaluation_prompt(text, question, user_answer, quiz_type="open-ended")


class ShortAnswerStrategy(QuizGenerationStrategy):
    """
    Modo Intermédio: Perguntas de resposta curta (Frase simples).
    Exige construção de frase, mas sem a complexidade de um texto longo.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        return quiz_prompts.get_short_answer_prompt(text, topics, priority_topics, material_topics)

    def generate_evaluation_prompt(self, text: str, question: str, user_answer: str) -> str:
        # Reusing the unified evaluation prompt with type hint
        return quiz_prompts.get_evaluation_prompt(text, question, user_answer, quiz_type="short_answer")

