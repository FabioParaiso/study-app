from modules.quizzes.prompts.templates import (
    MULTIPLE_CHOICE_TEMPLATE,
    OPEN_ENDED_TEMPLATE,
    SHORT_ANSWER_TEMPLATE,
    EVALUATION_TEMPLATE,
    COMMON_LANGUAGE_RULES,
    PERSONA_TEACHER
)


class PromptBuilder:
    """Constrói prompts de geração de quizzes (MCQ usa lista fixa; outros usam whitelist)."""

    @staticmethod
    def _build_topic_instruction(topics: list[str], material_concepts: list[str]) -> str:
        """Cria instruções de escopo para 0/1 tópico e whitelist."""
        topic_str = topics[0] if topics else "TODOS"
        vocab_str = ", ".join(material_concepts) if material_concepts else "Nenhum conceito detetado"
        list_block = f"""
            LISTA DE CONCEITOS:
            [{vocab_str}]"""

        if topics:
            return f"""ÂMBITO DE CONTEÚDO (FILTRADO):
            O utilizador quer estudar APENAS o tópico macro: [{topic_str}].
            {list_block}
            
            INSTRUÇÃO:
            - Usa APENAS os conceitos desta lista.
            - Cria perguntas DIVERSIFICADAS sobre estes conceitos."""
        else:
            return f"""ÂMBITO DE CONTEÚDO (GLOBAL - MODO REVISÃO):
            O utilizador quer um teste abrangente.
            {list_block}
            
            INSTRUÇÃO:
            - Usa APENAS os conceitos desta lista.
            - Cria perguntas DIVERSIFICADAS para cobrir diferentes áreas temáticas."""

    @staticmethod
    def _build_priority_instruction(priority_topics: list[str], min_questions: int = 2) -> str:
        """Gera instrução de prioridade; vazio se não houver tópicos prioritários."""
        if not priority_topics:
            return ""
        p_str = ", ".join(priority_topics)
        return f"\nATENÇÃO: O aluno tem DIFICULDADE nos seguintes tópicos: {p_str}. Cria pelo menos {min_questions} perguntas focadas neles para reforço."

    @staticmethod
    def _dedupe_list(items: list[str]) -> list[str]:
        """Remove duplicados (case-insensitive) preservando a ordem original."""
        seen: set[str] = set()
        unique: list[str] = []
        for item in items:
            norm = item.strip().lower()
            if not norm or norm in seen:
                continue
            seen.add(norm)
            unique.append(item)
        return unique

    @staticmethod
    def _build_vocab_instruction(material_concepts: list[str]) -> str:
        """Whitelist simples para prompts não-MCQ."""
        if not material_concepts:
            return ""
        v_str = ", ".join(material_concepts)
        return f"""LISTA DE CONCEITOS ACEITES:
        [{v_str}]
        - Cria perguntas APENAS para estes conceitos."""

    @staticmethod
    def _build_mcq_sequence_instruction(concepts: list[str]) -> str:
        """Lista ordenada: 1 linha = 1 pergunta (MCQ), permitindo repetições."""
        if not concepts:
            return ""
        lines = "\n".join(f"{idx}. {concept}" for idx, concept in enumerate(concepts, start=1))
        return f"""LISTA FINAL DE CONCEITOS (ORDEM FIXA):
        Cada linha corresponde a 1 pergunta. Gera exatamente {len(concepts)} perguntas e segue a ordem.
        Se um conceito aparecer mais do que uma vez, cria perguntas DIFERENTES em cada ocorrência.
        {lines}"""

    @classmethod
    def build_quiz_prompt(cls, quiz_type: str, text: str, topics: list[str], priority_topics: list[str] | None, material_concepts: list[str] | None) -> str:
        """Constrói o prompt final; MCQ usa sequência fixa, outros usam whitelist."""
        material_concepts = material_concepts or []
        topic_concepts = cls._dedupe_list(material_concepts)
        is_mcq = quiz_type == "multiple-choice"

        topic_instr = cls._build_topic_instruction(topics, topic_concepts)
        priority_instr = "" if is_mcq else cls._build_priority_instruction(priority_topics or [], min_questions=2)
        vocab_instr = cls._build_mcq_sequence_instruction(material_concepts) if is_mcq else cls._build_vocab_instruction(material_concepts)

        template = {
            "multiple-choice": MULTIPLE_CHOICE_TEMPLATE,
            "open-ended": OPEN_ENDED_TEMPLATE,
            "short_answer": SHORT_ANSWER_TEMPLATE
        }.get(quiz_type, MULTIPLE_CHOICE_TEMPLATE)

        return template.format(
            persona=PERSONA_TEACHER,
            topic_instruction=topic_instr,
            priority_instruction=priority_instr,
            vocab_instruction=vocab_instr,
            language_rules=COMMON_LANGUAGE_RULES,
            text=text[:50000]
        )


class EvaluationPromptBuilder:
    """Constrói prompts de avaliação de respostas (open-ended e short answer)."""

    @staticmethod
    def _get_model_answer_criteria_open() -> str:
        """Critérios da resposta modelo e curiosidade para resposta aberta."""
        return """- RESPOSTA MODELO (model_answer): 
            * OBRIGATÓRIA. MÁXIMO 50 PALAVRAS (2-3 frases curtas).
            * Linguagem ULTRA-SIMPLES para alunos do 5º ao 9º ano (11-15 anos).
            * Começa com o essencial: "O ar entra pelo nariz..." não "O sistema respiratório..."
            * 1 analogia simples no máximo (ex: "É como um tubo").
            * PROIBIDO: parágrafos longos, listas, palavras técnicas.
        - CURIOSIDADE (curiosity): 
            * OBRIGATÓRIA. 1 frase curta (máx. 15 palavras).
            * Formato: "Sabias que [facto curioso]?"
            * Só escreve a curiosity se a pontuação for < 100 ou se missing_points não estiver vazio.
            * Se a pontuação for 100 e missing_points = [], devolve "".
        """

    @staticmethod
    def _get_model_answer_criteria_short() -> str:
        """Critérios da resposta modelo e curiosidade para resposta curta."""
        return """- RESPOSTA MODELO (model_answer): 
            * OBRIGATÓRIA. 1 FRASE CURTA (8-15 palavras).
            * Linguagem simples para alunos do 5º ao 9º ano (11-15 anos).
            * Responde DIRETAMENTE ao que foi perguntado.
            * PROIBIDO: explicações longas, listas, termos técnicos.
            * Só escreve a model_answer se a pontuação for < 50 (se for >= 50, devolve "").
        - CURIOSIDADE (curiosity): 
            * OBRIGATÓRIA. 1 frase curta (máx. 15 palavras).
            * Formato: "Sabias que [facto curioso]?"
            * Só escreve a curiosity se a pontuação for < 100 ou se missing_points não estiver vazio.
            * Se a pontuação for 100 e missing_points = [], devolve "".
        """

    @staticmethod
    def _get_evaluation_json_format() -> str:
        """Esquema JSON esperado na avaliação."""
        return """SAÍDA (JSON):
            { 
                "score": 0-100,
                "feedback": "Frase motivacional curta (5-10 palavras).",
                "missing_points": ["Ponto curto 1", "Ponto curto 2"],
                "model_answer": "Resposta modelo (segue critérios acima; se não aplicável, usa \"\").",
                "curiosity": "Curiosidade curta (se aplicável; caso contrário \"\")."
            }"""

    @staticmethod
    def _get_scoring_rubric(quiz_type: str) -> str:
        """Guia curto de pontuação para tornar a nota consistente."""
        if quiz_type == "short_answer":
            return """- 100: Resposta correta, direta e com frase completa (Sujeito + Verbo).
- 70–90: Correta, mas falta 1 detalhe relevante.
- 40–60: Parcialmente correta; lacunas importantes ou frase pouco completa.
- 0–30: Incorreta, muito vaga ou não responde ao que foi perguntado."""
        return """- 100: Resposta correta e completa; responde exatamente ao pedido.
- 70–90: Correta, mas falta 1 detalhe relevante.
- 40–60: Parcialmente correta; lacunas importantes ou pouco clara.
- 0–30: Incorreta, muito vaga ou não responde à pergunta."""

    @staticmethod
    def _build_evaluation_context(text: str, question: str, user_answer: str) -> str:
        """Contexto de avaliação com matéria, pergunta e resposta do aluno."""
        return f"""CONTEXTO (Matéria):
            {text[:30000]}...

            PERGUNTA: "{question}"
            RESPOSTA DO ALUNO: "{user_answer}"""
    
    @classmethod
    def build(cls, text: str, question: str, user_answer: str, quiz_type: str = "open-ended") -> str:
        """Monta o prompt de avaliação, adaptado ao tipo de quiz."""
        context = cls._build_evaluation_context(text, question, user_answer)
        json_format = cls._get_evaluation_json_format()
        scoring_rubric = cls._get_scoring_rubric(quiz_type)

        extra_instructions = ""
        if quiz_type == "short_answer":
            extra_instructions = """
            IMPORTANTE (Resposta Curta):
            1. Verifica se a resposta está FACTUALMENTE CORRETA.
            2. Verifica se usou uma FRASE COMPLETA.
            3. Missing_points deve referir APENAS o que a pergunta pede (não pedir definições extra).
            """
            model_criteria = cls._get_model_answer_criteria_short()
        else:
            extra_instructions = """
            IMPORTANTE (Resposta Aberta):
            1. Avalia a resposta de 0 a 100.
            2. Dá feedback MOTIVACIONAL CURTO.
            """
            model_criteria = cls._get_model_answer_criteria_open()

        return EVALUATION_TEMPLATE.format(
            persona=PERSONA_TEACHER,
            context=context,
            extra_instructions=extra_instructions,
            language_rules=COMMON_LANGUAGE_RULES,
            model_criteria=model_criteria,
            scoring_rubric=scoring_rubric,
            json_format=json_format
        )
