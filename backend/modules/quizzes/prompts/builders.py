from modules.quizzes.prompts.templates import (
    MULTIPLE_CHOICE_TEMPLATE,
    OPEN_ENDED_TEMPLATE,
    SHORT_ANSWER_TEMPLATE,
    EVALUATION_TEMPLATE,
    COMMON_LANGUAGE_RULES,
    PERSONA_TEACHER
)


class PromptBuilder:
    @staticmethod
    def _build_topic_instruction(topics: list[str], material_concepts: list[str]) -> str:
        topic_str = ", ".join(topics) if topics else "TODOS"
        vocab_str = ", ".join(material_concepts) if material_concepts else "Nenhum conceito detetado (Erro)"

        if topics:
            return f"""ESCOPO DE CONTEÚDO (FILTRADO):
            O utilizador quer estudar APENAS os tópicos macro: [{topic_str}].

            BASE DE CONCEITOS (WHITELIST):
            [{vocab_str}]

            INSTRUÇÃO DE SELEÇÃO:
            1. Olha para a BASE DE CONCEITOS acima.
            2. Seleciona APENAS os conceitos dessa lista que pertencem logicamente aos tópicos [{topic_str}].
            3. Ignora tudo o resto.
            4. Cria perguntas DIVERSIFICADAS sobre esses conceitos filtrados."""
        else:
            return f"""ESCOPO DE CONTEÚDO (GLOBAL - MODO REVISÃO):
            O utilizador quer um teste abrangente.

            BASE DE CONCEITOS (WHITELIST):
            [{vocab_str}]

            INSTRUÇÃO DE COBERTURA:
            1. Usa a lista acima como o teu ÚNICO menu.
            2. Seleciona conceitos variados (início, meio, fim da lista).
            3. Garante que perguntas sobre conceitos de diferentes áreas temáticas."""

    @staticmethod
    def _build_priority_instruction(priority_topics: list[str], min_questions: int = 2) -> str:
        if not priority_topics:
            return ""
        p_str = ", ".join(priority_topics)
        return f"\nATENÇÃO: O aluno tem DIFICULDADE nos seguintes tópicos: {p_str}. Cria pelo menos {min_questions} perguntas focadas neles para reforço."

    @staticmethod
    def _build_vocab_instruction(material_concepts: list[str]) -> str:
        if not material_concepts:
            return ""
        v_str = ", ".join(material_concepts)
        return f"""BASE DE CONCEITOS ACEITES (WHITELIST):
        Ao criar perguntas, tens de escolher o 'alvo' DA LISTA ABAIXO.
        [{v_str}]
        - NÃO inventes conceitos novos. Usa apenas estes termos aprovados.
        - Se o utilizador pediu um Tópico Específico, escolhe desta lista os conceitos que pertencem a esse tópico."""

    @classmethod
    def build_quiz_prompt(cls, quiz_type: str, text: str, topics: list[str], priority_topics: list[str] | None, material_concepts: list[str]) -> str:
        topic_instr = cls._build_topic_instruction(topics, material_concepts or [])
        priority_instr = cls._build_priority_instruction(priority_topics or [], min_questions=4 if quiz_type == "multiple-choice" else 2)
        vocab_instr = cls._build_vocab_instruction(material_concepts or [])

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
    @staticmethod
    def _get_model_answer_criteria() -> str:
        return """- RESPOSTA MODELO (model_answer): 
            * OBRIGATÓRIA. MÁXIMO 50 PALAVRAS (2-3 frases curtas).
            * Linguagem ULTRA-SIMPLES para criança de 10 anos.
            * Começa com o essencial: "O ar entra pelo nariz..." não "O sistema respiratório..."
            * 1 analogia simples no máximo (ex: "É como um tubo").
            * PROIBIDO: parágrafos longos, listas, palavras técnicas.
            - CURIOSIDADE (curiosity): 
            * 1 frase curta APENAS (máx. 15 palavras).
            * Formato: "Sabias que [facto curioso]?"""

    @staticmethod
    def _get_evaluation_json_format() -> str:
        return """SAÍDA (JSON):
            { 
                "score": 0-100,
                "feedback": "Frase motivacional curta (5-10 palavras).",
                "missing_points": ["Ponto curto 1", "Ponto curto 2"],
                "model_answer": "Resposta simples em 2-3 frases curtas. Máximo 50 palavras!",
                "curiosity": "Sabias que [facto curto]?"
            }"""

    @staticmethod
    def _build_evaluation_context(text: str, question: str, user_answer: str) -> str:
        return f"""CONTEXTO (Matéria):
            {text[:30000]}...

            PERGUNTA: "{question}"
            RESPOSTA DO ALUNO: "{user_answer}\""""
    
    @classmethod
    def build(cls, text: str, question: str, user_answer: str, quiz_type: str = "open-ended") -> str:
        context = cls._build_evaluation_context(text, question, user_answer)
        model_criteria = cls._get_model_answer_criteria()
        json_format = cls._get_evaluation_json_format()

        extra_instructions = ""
        if quiz_type == "short_answer":
            extra_instructions = """
            IMPORTANT (Short Answer):
            1. Verifica se a resposta está FACTUALMENTE CORRETA.
            2. Verifica se usou uma FRASE COMPLETA.
            """
        else:
            extra_instructions = """
            IMPORTANT (Open Ended):
            1. Avalia a resposta de 0 a 100.
            2. Dá feedback MOTIVACIONAL CURTO.
            """

        return EVALUATION_TEMPLATE.format(
            persona=PERSONA_TEACHER,
            context=context,
            extra_instructions=extra_instructions,
            language_rules=COMMON_LANGUAGE_RULES,
            model_criteria=model_criteria,
            json_format=json_format
        )
