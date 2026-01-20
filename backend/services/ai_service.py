from openai import OpenAI
import json
from .quiz_strategies import QuizGenerationStrategy

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

        prompt = f"""
        Atua como um professor a corrigir um teste.
        
        CONTEXTO (Matéria):
        {text[:30000]}...

        PERGUNTA: "{question}"
        RESPOSTA DO ALUNO: "{user_answer}"

        TAREFA:
        Avalia a resposta do aluno de 0 a 100 com base na correção factual e completude face ao texto.

        CRITÉRIOS DE FEEDBACK (PT-PT):
        - Sê justo. Se a resposta demonstrar compreensão do conceito, dá boa nota mesmo com erros ligeiros.
        - Se a nota for < 100, explica O QUE faltou ou O QUE está errado.
        - Começa com uma palavra encorajadora (Ex: "Boa!", "Quase!", "Excelente!") se a nota for positiva (>50).
        - Usa "Tu" (PT-PT).

        SAÍDA (JSON):
        {{ "score": 0-100, "feedback": "Feedback pedagógico curto (máx 2 frases)." }}
        """

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

        existing_topics_str = ", ".join(existing_topics) if existing_topics else "Nenhum"

        prompt = f"""
        Atua como um assistente de organização de estudo.
        
        OBJETIVO:
        Identificar os tópicos principais abordados no texto fornecido.
        
        REGRAS DE DEDUPLICAÇÃO (CRÍTICO):
        Abaixo está uma lista de tópicos que JÁ EXISTEM na base de dados do aluno.
        TÓPICOS EXISTENTES: [{existing_topics_str}]
        
        1. Se o texto abordar um tópico que já existe na lista acima (mesmo que com nome ligeiramente diferente), DEVES usar o nome EXATO da lista existente.
           Exemplo: Se existe "Biologia Celular" e o texto fala de "Células", usa "Biologia Celular".
        2. Cria NOVOS tópicos apenas se o conceito for substancialmente novo e não encaixar nos existentes.
        3. Sê conciso. Retorna apenas tópicos de alto nível (máximo 5).
        
        TEXTO PARA ANÁLISE:
        {text[:15000]}...

        SAÍDA (JSON):
        {{ "topics": ["Tópico A", "Tópico B"] }}
        """

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
            return data.get("topics", [])
        except Exception as e:
            print(f"Error extracting topics: {e}")
            return ["Tópicos Gerais"]
