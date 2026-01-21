from abc import ABC, abstractmethod
import json


class QuizGenerationStrategy(ABC):
    """
    Classe base abstrata para estratégias de geração de quizzes.
    Contém métodos auxiliares partilhados para construir instruções dinâmicas.
    """

    def _build_topic_instruction(self, topics: list[str]) -> str:
        """Constrói instrução para filtrar por tópicos selecionados."""
        if not topics or len(topics) == 0:
            return ""
        topic_str = ", ".join(topics)
        # Clear and concise instruction - the priority_topics conflict is now handled upstream
        return f"""FILTRAGEM DE TÓPICO: O utilizador selecionou [{topic_str}]. 
        Gera perguntas APENAS sobre este tópico. Ignora o resto do texto."""

    def _build_priority_instruction(self, priority_topics: list[str], min_questions: int = 2) -> str:
        """Constrói instrução para focar em tópicos com dificuldade."""
        if not priority_topics or len(priority_topics) == 0:
            return ""
        p_str = ", ".join(priority_topics)
        return f"\nATENÇÃO: O aluno tem DIFICULDADE nos seguintes tópicos: {p_str}. Cria pelo menos {min_questions} perguntas focadas neles para reforço."

    def _build_vocab_instruction(self, material_topics: list[str]) -> str:
        """Constrói instrução para manter consistência de vocabulário de tópicos."""
        if not material_topics or len(material_topics) == 0:
            return ""
        v_str = ", ".join(material_topics)
        return f"\nCONSISTÊNCIA DE TÓPICOS: Ao categorizar cada pergunta no campo JSON 'topic', NUNCA inventes novos nomes. Usa APENAS um dos seguintes: [{v_str}]. Escolhe o que melhor se adapta."

    def _get_common_language_rules(self) -> str:
        """Regras de linguagem partilhadas (PT-PT, termos proibidos, idade)."""
        return """
        LINGUAGEM (PT-PT ESTRITO):
        - ADEQUA A LINGUAGEM PARA CRIANÇAS DE 10-12 ANOS (Frases curtas e diretas).
        - Português de Portugal APENAS.
        - PROIBIDO GERÚNDIO: Nunca uses "fazendo", "correndo". Usa "a fazer", "a correr".
        - PROIBIDO BRASILEIRISMO: "Úmido"→"Húmido", "Celular"→"Telemóvel", "Ônibus"→"Autocarro", "Tela"→"Ecrã", "Time"→"Equipa", "Arquivo"→"Ficheiro", "Esporte"→"Desporto", "Usuário"→"Utilizador".
        - Tratamento por "Tu". Nunca "Você".
        """

    def _get_persona_instruction(self) -> str:
        """Persona do professor partilhada."""
        return "Atua como um professor do 6º ano super motivador (estilo YouTuber fixe)."

    def _build_base_instructions(self, topics: list[str], priority_topics: list[str], material_topics: list[str], min_priority_questions: int = 2) -> tuple:
        """
        Constrói todas as instruções base para um prompt de geração.
        Retorna tupla: (topic_instruction, priority_instruction, vocab_instruction, persona, language_rules)
        """
        return (
            self._build_topic_instruction(topics),
            self._build_priority_instruction(priority_topics, min_questions=min_priority_questions),
            self._build_vocab_instruction(material_topics),
            self._get_persona_instruction(),
            self._get_common_language_rules()
        )

    def _get_model_answer_criteria(self) -> str:
        """Critérios partilhados para a resposta modelo nos prompts de avaliação."""
        return """- RESPOSTA MODELO (model_answer): 
          * OBRIGATÓRIA. MÁXIMO 50 PALAVRAS (2-3 frases curtas).
          * Linguagem ULTRA-SIMPLES para criança de 10 anos.
          * Começa com o essencial: "O ar entra pelo nariz..." não "O sistema respiratório..."
          * 1 analogia simples no máximo (ex: "É como um tubo").
          * PROIBIDO: parágrafos longos, listas, palavras técnicas.
        - CURIOSIDADE (curiosity): 
          * 1 frase curta APENAS (máx. 15 palavras).
          * Formato: "Sabias que [facto curioso]?\""""

    def _get_evaluation_json_format(self) -> str:
        """Formato JSON de saída partilhado para prompts de avaliação."""
        return """SAÍDA (JSON):
        { 
            "score": 0-100,
            "feedback": "Frase motivacional curta (5-10 palavras).",
            "missing_points": ["Ponto curto 1", "Ponto curto 2"],
            "model_answer": "Resposta simples em 2-3 frases curtas. Máximo 50 palavras!",
            "curiosity": "Sabias que [facto curto]?"
        }"""

    def _build_evaluation_context(self, text: str, question: str, user_answer: str) -> str:
        """Constrói o bloco de contexto comum para prompts de avaliação."""
        return f"""CONTEXTO (Matéria):
        {text[:30000]}...

        PERGUNTA: "{question}"
        RESPOSTA DO ALUNO: "{user_answer}\""""

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
        topic_instruction, priority_instruction, vocab_instruction, persona, language_rules = \
            self._build_base_instructions(topics, priority_topics, material_topics, min_priority_questions=4)

        return f"""
        {topic_instruction}

        {persona}. Cria um Quiz de 10 perguntas de escolha múltipla SIMPLES.

        {priority_instruction}
        {vocab_instruction}

        OBJETIVO: APRENDER A BRINCAR
        O objetivo é ajudar o aluno a perceber os conceitos sem sentir que está num teste aborrecido.
        
        REGRAS DE OURO PARA AS PERGUNTAS (FEW-SHOT):
        1. Foca-te na COMPREENSÃO, não na memorização.
           ❌ MAU: "Em que ano foi assinada a independência?" (Memorização seca)
           ✅ BOM: "Porque é que a independência foi importante para o povo?" (Compreensão)
        2. Usa situações práticas sempre que possível.
           ✅ BOM: "Se deixares uma planta no escuro, o que lhe acontece?"

        REGRAS PARA AS OPÇÕES (DISTRATORES):
        1. As opções erradas devem ser ERROS COMUNS de raciocínio.
        2. PROIBIDO usar "Nenhuma das anteriores" ou "Todas as anteriores".
        3. As opções devem ter comprimentos semelhantes.
        4. NÃO use prefixos como "A)", "B)" no texto das opções.

        CRITÉRIOS DE EXPLICAÇÃO (MODELO MENTAL):
        - Explica COMO se chega à resposta correta.
        - Começa com "Sabias que..." ou "Imagina que..." sempre que possível.
        - Usa ANALOGIAS DO DIA-A-DIA (ex: comparar a célula a uma fábrica ou cidade).
        - O tom deve ser positivo, curioso e fácil de ler.

        {language_rules}
        - ESCRITA COMO SE FOSSES UM YOUTUBER A EXPLICAR ALGO FIXE.

        FORMATO DE SAÍDA (JSON ESTRITO):
        Retorna APENAS um objeto JSON com a chave "questions".
        {{
            "questions": [
                {{
                    "topic": "Tópico Específico",
                    "question": "Pergunta interessante?",
                    "options": ["Opção Plausível A", "Opção Plausível B", "Opção Correta", "Opção Plausível C"],
                    "correctIndex": 2,
                    "explanation": "Sabias que... [Explicação divertida com analogia ou curiosidade]"
                }}
            ]
        }}

        TEXTO DE ESTUDO:
        {text[:50000]}
        """


class OpenEndedStrategy(QuizGenerationStrategy):
    """
    Modo Avançado: Perguntas de resposta aberta.
    Exige pensamento crítico seguindo a Taxonomia de Bloom.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        topic_instruction, priority_instruction, vocab_instruction, persona, language_rules = \
            self._build_base_instructions(topics, priority_topics, material_topics, min_priority_questions=1)

        return f"""
        {topic_instruction}

        {persona}. Cria um mini-teste de 5 perguntas de resposta aberta.

        {priority_instruction}
        {vocab_instruction}

        REGRAS (TAXONOMIA DE BLOOM):
        Distribui as 5 perguntas assim:
        - 2 de COMPREENDER: "Explica por palavras tuas...", "O que significa...?"
        - 2 de ANALISAR/APLICAR: "Dá um exemplo prático de...", "Compara..."
        - 1 de AVALIAR/CRIAR: "Na tua opinião...", "Como resolverias...?"
        Evita perguntas de "sim/não". Cada resposta deve ser explicativa (1-2 frases).

        EXEMPLOS DE PERGUNTAS (CALIBRAÇÃO):
        ❌ MAU (Vago): "Fala-me sobre a fotossíntese." (O aluno não sabe por onde começar)
        ❌ MAU (Fechado): "A fotossíntese usa luz?" (Responde-se com Sim/Não)
        ✅ BOM (Equilibrado): "Explica, por palavras tuas, porque é que a fotossíntese é essencial para a vida na Terra."

        {language_rules}

        FORMATO DE SAÍDA (JSON):
        {{ 
            "questions": [
                {{ "topic": "Tema", "question": "Questão..." }}
            ] 
        }}

        TEXTO:
        {text[:50000]}
        """

    def generate_evaluation_prompt(self, text: str, question: str, user_answer: str) -> str:
        language_rules = self._get_common_language_rules()
        persona = self._get_persona_instruction()
        context = self._build_evaluation_context(text, question, user_answer)
        model_criteria = self._get_model_answer_criteria()
        json_format = self._get_evaluation_json_format()
        
        return f"""
        {persona}.
        O teu objetivo é AJUDAR o aluno a aprender, não apenas avaliar.
        
        {context}

        TAREFA:
        1. Avalia a resposta de 0 a 100.
        2. Dá feedback MOTIVACIONAL CURTO.
        3. Identifica O QUE FALTOU referir (missing_points).
        4. Cria uma RESPOSTA MODELO COMPLETA (model_answer).
        5. Cria uma CURIOSIDADE separada.

        {language_rules}

        CRITÉRIOS DE AVALIAÇÃO ESPECÍFICOS:
        - SE A NOTA FOR 100: 'missing_points' = [].
        - SE A NOTA FOR < 100: 'missing_points' = ["Faltou referir X", "Não disseste Y"].
        {model_criteria}

        {json_format}
        """


class ShortAnswerStrategy(QuizGenerationStrategy):
    """
    Modo Intermédio: Perguntas de resposta curta (Frase simples).
    Exige construção de frase, mas sem a complexidade de um texto longo.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_topics: list[str] = None) -> str:
        topic_instruction, priority_instruction, vocab_instruction, persona, language_rules = \
            self._build_base_instructions(topics, priority_topics, material_topics, min_priority_questions=2)

        return f"""
        {topic_instruction}

        {persona}. Cria um mini-teste de 8 perguntas de RESPOSTA CURTA (FRASE SIMPLES).

        {priority_instruction}
        {vocab_instruction}

        OBJETIVO: TREINO DE SINTAXE E FACTOS
        O objetivo deste nível (Intermédio) é garantir que o aluno sabe construir uma frase completa com Sujeito e Verbo. Não queremos ainda reflexões profundas.

        REGRAS DE CRIAÇÃO (SINTAXE vs CONTEÚDO):
        1. Foca-te em FACTOS CONCRETOS (O quê, Quem, Onde, Como).
           ❌ PROIBIDO: Perguntas de "Porquê" complexo ou "Opinião" (Isso é para o Nível Avançado).
        2. A resposta ideal deve ter SUJEITO e VERBO explícitos.
           ❌ MAU: "Qual o nome do processo?" (Resposta: "Fotossíntese" -> 1 palavra, Errado para este nível)
           ✅ BOM: "O que fazem as plantas na fotossíntese?" (Resposta: "As plantas produzem o seu alimento.")
        3. Tamanho da resposta esperada: 5 a 15 palavras.

        ⚠️ ATENÇÃO CRÍTICA - FORMATO DA PERGUNTA:
        - O campo 'question' deve conter uma FRASE INTERROGATIVA (termina com ?).
        - NUNCA coloques uma afirmação ou resposta no campo 'question'.
        - CORRETO: "Como é o sistema digestivo dos ruminantes?"
        - ERRADO: "O estômago tem quatro compartimentos." (Isto é uma afirmação!)

        {language_rules}

        FORMATO DE SAÍDA (JSON):
        {{ 
            "questions": [
                {{ 
                    "topic": "Tema",
                    "question": "Pergunta que exige frase simples? (DEVE TERMINAR COM ?)"
                }}
            ] 
        }}

        TEXTO:
        {text[:50000]}
        """

    def generate_evaluation_prompt(self, text: str, question: str, user_answer: str) -> str:
        language_rules = self._get_common_language_rules()
        persona = self._get_persona_instruction()
        context = self._build_evaluation_context(text, question, user_answer)
        model_criteria = self._get_model_answer_criteria()
        json_format = self._get_evaluation_json_format()
        
        return f"""
        {persona}.
        O objetivo é dar feedback que ajude a melhorar a literacia, mas que deixe o aluno FELIZ.

        {context}

        TAREFA:
        1. Verifica se a resposta está FACTUALMENTE CORRETA.
        2. Verifica se usou uma FRASE COMPLETA.
        3. Identifica O QUE FALTOU (missing_points).
        4. Cria uma RESPOSTA MODELO COMPLETA (model_answer).
        5. Cria uma CURIOSIDADE separada.

        {language_rules}

        CRITÉRIOS DE AVALIAÇÃO ESPECÍFICOS:
        - SE A NOTA FOR 100: 'missing_points' = [].
        - SE A NOTA FOR < 100: 'missing_points' = ["Faltou referir X", "Não disseste Y"].
        {model_criteria}

        {json_format}
        """
