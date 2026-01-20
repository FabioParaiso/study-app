class AnswerEvaluator:
    @staticmethod
    def generate_prompt(text: str, question: str, user_answer: str) -> str:
        return f"""
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
