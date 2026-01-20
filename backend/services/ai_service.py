from openai import OpenAI
import json

class AIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_quiz(self, text: str, topics: list[str] = None, priority_topics: list[str] = None) -> list[dict]:
        if not self.client: return None
        
        topic_instruction = ""
        if topics and len(topics) > 0:
            topic_str = ", ".join(topics)
            topic_instruction = f"INSTRUÇÃO CRÍTICA: O utilizador selecionou TÓPICOS ESPECÍFICOS: {topic_str}. Tens de gerar perguntas APENAS relacionadas com estes tópicos. Ignora todas as outras secções do texto."

        priority_instruction = ""
        if priority_topics and len(priority_topics) > 0:
            p_str = ", ".join(priority_topics)
            priority_instruction = f"\nATENÇÃO: O aluno tem DIFICULDADE nos seguintes tópicos: {p_str}. Cria pelo menos 3 perguntas focadas neles para reforço."

        prompt = f"""
        Atua como um professor experiente e pedagógico do 6º ano.
        Com base no texto fornecido, cria um Quiz de 10 perguntas de escolha múltipla.

        {topic_instruction}
        {priority_instruction}

        REGRAS DE CRIAÇÃO:
        1. Cria 10 perguntas focadas na compreensão de conceitos-chave.
        2. As opções incorretas (distratores) devem ser plausíveis, evitando opções obviamente erradas ou ridículas.
        3. Apenas uma opção deve ser inequivocamente correta.
        4. Varia o tipo de perguntas (Definição, Identificação, Raciocínio).

        CRITÉRIOS DE LINGUAGEM (PT-PT):
        - Usa Português de Portugal correto (e.g., "Ecrã" e não "Tela", "Ficheiro" e não "Arquivo").
        - Trata o aluno por "Tu" ou usa impessoal. Nunca uses "Você".
        - Tom encorajador e claro.

        FORMATO DE SAÍDA (JSON ESTRITO):
        Retorna APENAS um objeto JSON com a chave "questions".
        {{
            "questions": [
                {{
                    "topic": "Tópico Específico da Pergunta",
                    "question": "Enunciado da pergunta?",
                    "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
                    "correctIndex": 0,
                    "explanation": "Explicação breve e didática sobre a resposta correta."
                }}
            ]
        }}

        TEXTO DE ESTUDO:
        {text[:50000]}
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
            return data.get("questions", [])
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return None

    def generate_open_questions(self, text: str, topics: list[str] = None) -> list[dict]:
        if not self.client: return None

        topic_instruction = ""
        if topics and len(topics) > 0:
            topic_str = ", ".join(topics)
            topic_instruction = f"INSTRUÇÃO CRÍTICA: O utilizador selecionou TÓPICOS ESPECÍFICOS: {topic_str}. Tens de gerar perguntas APENAS relacionadas com estes tópicos. Ignora todas as outras secções do texto."

        prompt = f"""
        Atua como um professor experiente. Cria um mini-teste de 5 perguntas de resposta aberta.

        {topic_instruction}

        REGRAS:
        1. Cria exatamente 5 perguntas que exijam uma resposta explicativa curta (1-2 frases).
        2. Foca-te nos conceitos mais importantes do texto.
        3. Evita perguntas de "sim/não".

        LINGUAGEM (PT-PT):
        - Português de Portugal.
        - Tratamento por "Tu".

        FORMATO DE SAÍDA (JSON):
        {{ 
            "questions": [
                {{ "topic": "Tema", "question": "Questão..." }}
            ] 
        }}

        TEXTO:
        {text[:50000]}
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
            return data.get("questions", [])
        except Exception as e:
            print(f"Error generating open questions: {e}")
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
