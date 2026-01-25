from abc import ABC, abstractmethod
import json
from modules.quizzes.prompts.builders import PromptBuilder, EvaluationPromptBuilder


class QuizGenerationStrategy(ABC):
    """
    Classe base abstrata para estratégias de geração de quizzes.
    Delega a construção do prompt para o PromptBuilder.
    """

    @abstractmethod
    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_concepts: list[str] = None) -> str:
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

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_concepts: list[str] = None) -> str:
        return PromptBuilder.build_quiz_prompt(
            quiz_type="multiple-choice",
            text=text,
            topics=topics,
            priority_topics=priority_topics,
            material_concepts=material_concepts
        )


class OpenEndedStrategy(QuizGenerationStrategy):
    """
    Modo Avançado: Perguntas de resposta aberta.
    Exige pensamento crítico seguindo a Taxonomia de Bloom.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_concepts: list[str] = None) -> str:
        return PromptBuilder.build_quiz_prompt(
            quiz_type="open-ended",
            text=text,
            topics=topics,
            priority_topics=priority_topics,
            material_concepts=material_concepts
        )

    def generate_evaluation_prompt(self, text: str, question: str, user_answer: str) -> str:
        return EvaluationPromptBuilder.build(text, question, user_answer, quiz_type="open-ended")


class ShortAnswerStrategy(QuizGenerationStrategy):
    """
    Modo Intermédio: Perguntas de resposta curta (Frase simples).
    Exige construção de frase, mas sem a complexidade de um texto longo.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_concepts: list[str] = None) -> str:
        return PromptBuilder.build_quiz_prompt(
            quiz_type="short_answer",
            text=text,
            topics=topics,
            priority_topics=priority_topics,
            material_concepts=material_concepts
        )

    def generate_evaluation_prompt(self, text: str, question: str, user_answer: str) -> str:
        return EvaluationPromptBuilder.build(text, question, user_answer, quiz_type="short_answer")
