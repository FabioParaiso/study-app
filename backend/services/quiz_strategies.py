from abc import ABC, abstractmethod
import json

class QuizGenerationStrategy(ABC):
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
        Atua como um professor do 6º ano altamente motivador e empático. Cria um Quiz de 10 perguntas de escolha múltipla SIMPLES.

        {topic_instruction}
        {priority_instruction}
        {vocab_instruction}

        OBJETIVO: APRENDER A BRINCAR
        O objetivo é ajudar o aluno a perceber os conceitos sem sentir que está num teste aborrecido.
        
        REGRAS DE CRIAÇÃO:
        - Foca em perguntas DIRETAS sobre conceitos.
        - Evita rasteiras. O objetivo é que o aluno se sinta inteligente.
        - Cada pergunta deve ter UMA resposta claramente correta.
        - Os distratores (opções erradas) devem ser plausíveis mas claramente incorretos.

        CRITÉRIOS DE EXPLICAÇÃO (MUITO IMPORTANTE):
        - A explicação deve ser para uma criança de 10-12 anos.
        - USA PALAVRAS SIMPLES. Se usares uma palavra difícil, explica-a.
        - FRASES CURTAS e diretas. Máximo 15 palavras por frase.
        - Começa com "Sabias que..." ou "Imagina que..." sempre que possível.
        - Usa ANALOGIAS DO DIA-A-DIA (ex: comparar a célula a uma casa feita de tijolos).
        - O tom deve ser positivo, curioso e fácil de ler.

        CRITÉRIOS DE LINGUAGEM (PT-PT OBRIGATÓRIO):
        - Usa Português de Portugal APENAS (PT-PT).
        - Trata o aluno por "Tu".
        - PROIBIDO: Frases longas, termos técnicos sem explicação, voz passiva complexa.
        - ESCRITA COMO SE FOSSES UM YOUTUBER A EXPLICAR ALGO FIXE.

        FORMATO DE SAÍDA (JSON ESTRITO):
        Retorna APENAS um objeto JSON com a chave "questions".
        {{
            "questions": [
                {{
                    "topic": "Tópico Específico",
                    "question": "Pergunta?",
                    "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
                    "correctIndex": 0,
                    "explanation": "Sabias que... [Explicação divertida com analogia ou curiosidade]"
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

        priority_instruction = ""
        if priority_topics and len(priority_topics) > 0:
            p_str = ", ".join(priority_topics)
            priority_instruction = f"\nATENÇÃO: O aluno tem DIFICULDADE nos seguintes tópicos: {p_str}. Cria pelo menos 2 perguntas focadas neles para reforço."

        vocab_instruction = ""
        if material_topics and len(material_topics) > 0:
            v_str = ", ".join(material_topics)
            vocab_instruction = f"\nCONSISTÊNCIA DE TÓPICOS: Ao categorizar cada pergunta no campo JSON 'topic', NUNCA inventes novos nomes. Usa APENAS um dos seguintes: [{v_str}]."

        return f"""
        Atua como um professor experiente. Cria um mini-teste de 5 perguntas de resposta aberta.

        {topic_instruction}
        {priority_instruction}
        {vocab_instruction}

        REGRAS (TAXONOMIA DE BLOOM):
        Distribui as 5 perguntas assim:
        - 2 de COMPREENDER: "Explica por palavras tuas...", "O que significa...?"
        - 2 de ANALISAR/APLICAR: "Dá um exemplo prático de...", "Compara..."
        - 1 de AVALIAR/CRIAR: "Na tua opinião...", "Como resolverias...?"
        Evita perguntas de "sim/não". Cada resposta deve ser explicativa (1-2 frases).

        LINGUAGEM (PT-PT OBRIGATÓRIO):
        - Português de Portugal APENAS.
        - PROIBIDO termos brasileiros: "Úmido"→"Húmido", "Celular"→"Telemóvel", "Ônibus"→"Autocarro", "Tela"→"Ecrã".
        - Tratamento por "Tu". Nunca "Você".

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

class ShortAnswerStrategy(QuizGenerationStrategy):
    """
    Modo Intermédio: Perguntas de resposta curta (Frase simples).
    Exige construção de frase, mas sem a complexidade de um texto longo.
    """
    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        topic_instruction = ""
        if topics and len(topics) > 0:
            topic_str = ", ".join(topics)
            topic_instruction = f"INSTRUÇÃO CRÍTICA: O utilizador selecionou TÓPICOS ESPECÍFICOS: {topic_str}. Gera perguntas APENAS destes tópicos."

        priority_instruction = ""
        if priority_topics and len(priority_topics) > 0:
            p_str = ", ".join(priority_topics)
            priority_instruction = f"\nATENÇÃO: O aluno tem DIFICULDADE nos seguintes tópicos: {p_str}. Tenta incluir perguntas sobre estes temas."

        vocab_instruction = ""
        if material_topics and len(material_topics) > 0:
            v_str = ", ".join(material_topics)
            vocab_instruction = f"\nCONSISTÊNCIA DE TÓPICOS: Usa APENAS um dos seguintes: [{v_str}]."

        return f"""
        Atua como um professor do 6º ano. Cria um mini-teste de 8 perguntas de RESPOSTA CURTA (FRASE SIMPLES).

        {topic_instruction}
        {priority_instruction}
        {vocab_instruction}

        REGRAS IMPORTANTES:
        1. Cada pergunta deve exigir uma resposta de UMA FRASE SIMPLES (5 a 15 palavras).
        2. NÃO aceites respostas de apenas 1 palavra. A pergunta deve ser formulada para evitar isso.
        3. Exemplo: 
           - MAU: "Qual o nome do processo...?" (Resposta: Fotossíntese)
           - BOM: "O que acontece durante a fotossíntese?" (Resposta: As plantas usam a luz solar para criar energia.)
        4. O objetivo é treinar a literacia e a construção de frases.

        LINGUAGEM (PT-PT OBRIGATÓRIO):
        - Português de Portugal APENAS.
        - PROIBIDO termos brasileiros: "Úmido"→"Húmido", "Celular"→"Telemóvel", "Ônibus"→"Autocarro", "Tela"→"Ecrã".
        - Tratamento por "Tu". Nunca "Você".

        FORMATO DE SAÍDA (JSON):
        {{ 
            "questions": [
                {{ 
                    "topic": "Tema",
                    "question": "Pergunta que exige frase simples?",
                }}
            ] 
        }}

        TEXTO:
        {text[:50000]}
        """

    def parse_response(self, response_content: str) -> list[dict]:
        data = json.loads(response_content)
        return data.get("questions", [])

