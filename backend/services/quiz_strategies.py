from abc import ABC, abstractmethod
import json

class QuizGenerationStrategy(ABC):
    @abstractmethod
    @abstractmethod
    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        pass

    @abstractmethod
    def parse_response(self, response_content: str) -> list[dict]:
        pass

class MultipleChoiceStrategy(QuizGenerationStrategy):
    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        topic_instruction = ""
        if topics and len(topics) > 0:
            topic_str = ", ".join(topics)
            topic_instruction = f"INSTRUÇÃO CRÍTICA: O utilizador selecionou TÓPICOS ESPECÍFICOS: {topic_str}. Tens de gerar perguntas APENAS relacionadas com estes tópicos. Ignora todas as outras secções do texto."

        priority_instruction = ""
        if priority_topics and len(priority_topics) > 0:
            p_str = ", ".join(priority_topics)
            priority_instruction = f"\nATENÇÃO: O aluno tem DIFICULDADE nos seguintes tópicos: {p_str}. Cria pelo menos 3 perguntas focadas neles para reforço."

        vocab_instruction = ""
        if material_topics and len(material_topics) > 0:
            v_str = ", ".join(material_topics)
            vocab_instruction = f"\nCONSISTÊNCIA DE TÓPICOS: Ao categorizar cada pergunta no campo JSON 'topic', NUNCA inventes novos nomes. Usa APENAS um dos seguintes: [{v_str}]. Escolhe o que melhor se adapta."

        return f"""
        Atua como um professor experiente e pedagógico do 6º ano.
        Com base no texto fornecido, cria um Quiz de 10 perguntas de escolha múltipla.

        {topic_instruction}
        {priority_instruction}
        {vocab_instruction}

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

    def parse_response(self, response_content: str) -> list[dict]:
        data = json.loads(response_content)
        return data.get("questions", [])

class OpenEndedStrategy(QuizGenerationStrategy):
    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        topic_instruction = ""
        if topics and len(topics) > 0:
            topic_str = ", ".join(topics)
            topic_instruction = f"INSTRUÇÃO CRÍTICA: O utilizador selecionou TÓPICOS ESPECÍFICOS: {topic_str}. Tens de gerar perguntas APENAS relacionadas com estes tópicos. Ignora todas as outras secções do texto."

        vocab_instruction = ""
        if material_topics and len(material_topics) > 0:
            v_str = ", ".join(material_topics)
            vocab_instruction = f"\nCONSISTÊNCIA DE TÓPICOS: Ao categorizar cada pergunta no campo JSON 'topic', NUNCA inventes novos nomes. Usa APENAS um dos seguintes: [{v_str}]."

        return f"""
        Atua como um professor experiente. Cria um mini-teste de 5 perguntas de resposta aberta.

        {topic_instruction}
        {vocab_instruction}

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

    def parse_response(self, response_content: str) -> list[dict]:
        data = json.loads(response_content)
        return data.get("questions", [])
