class AnswerEvaluator:
    @staticmethod
    def generate_prompt(text: str, question: str, user_answer: str) -> str:
        return f"""
        Atua como um professor a corrigir um teste. O teu objetivo é AJUDAR o aluno a aprender, não apenas avaliar.
        
        CONTEXTO (Matéria):
        {text[:30000]}...

        PERGUNTA: "{question}"
        RESPOSTA DO ALUNO: "{user_answer}"

        TAREFA:
        1. Avalia a resposta do aluno de 0 a 100 com base na correção factual e completude.
        2. Fornece feedback construtivo focado no RACIOCÍNIO, não apenas no resultado.
        3. Cria uma RESPOSTA MODELO que explique o porquê, não apenas o quê.

        CRITÉRIOS DE FEEDBACK (PT-PT ESTRITO):
        - Sê justo. Se a resposta demonstrar compreensão do conceito, dá boa nota mesmo com erros ligeiros.
        - Se a nota for < 100, explica O QUE faltou ou O QUE está errado E PORQUÊ.
        - Começa com uma palavra encorajadora (Ex: "Boa!", "Quase!", "Excelente!") se a nota for positiva (>50).
        - Usa "Tu" (PT-PT). Nunca uses "Você".
        - A resposta modelo deve ser formulada de forma DIFERENTE da pergunta, para evitar memorização.

        SAÍDA (JSON):
        {{ 
            "score": 0-100, 
            "feedback": "Feedback pedagógico curto (máx 2 frases). Foca no raciocínio.",
            "model_answer": "Uma resposta ideal de 2-3 frases que explique o PORQUÊ e não seja apenas 'decorável'."
        }}
        """

    @staticmethod
    def generate_simple_answer_prompt(text: str, question: str, user_answer: str) -> str:
        return f"""
        Atua como um professor do 6º ano a corrigir uma resposta curta. 
        O objetivo é verificar se o aluno sabe o conceito E se construiu uma FRASE CORRETA.

        CONTEXTO (Matéria):
        {text[:30000]}...

        PERGUNTA: "{question}"
        RESPOSTA DO ALUNO: "{user_answer}"

        TAREFA:
        1. Verifica se a resposta está FACTUALMENTE CORRETA.
        2. Verifica se a resposta é uma FRASE COMPLETA (sujeito + verbo). 
           - APENAS palavras soltas (ex: "Fotossíntese") devem ter penalização leve, mas aviso claro.
           - O ideal é: "A fotossíntese é o processo..."

        CRITÉRIOS DE AVALIAÇÃO:
        - Se a resposta estiver errada -> Nota 0.
        - Se estiver certa mas for apenas 1 palavra -> Nota 70 (avisa para fazer frase).
        - Se estiver certa e for uma frase completa -> Nota 100.
        
        SAÍDA (JSON):
        {{ 
            "score": 0-100, 
            "feedback": "Feedback curto. Se for apenas 1 palavra, diz 'Tenta responder com uma frase completa da próxima vez!'." 
        }}
        """


class ShortAnswerEvaluator:
    """
    Avaliador para respostas curtas usando correspondência fuzzy.
    Não usa IA - é instantâneo!
    """
    @staticmethod
    def normalize(text: str) -> str:
        """Remove acentos, espaços extra e converte para minúsculas."""
        import unicodedata
        if not text:
            return ""
        # Normalize unicode and remove accents
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        return text.lower().strip()

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calcula a distância de Levenshtein entre duas strings."""
        if len(s1) < len(s2):
            return ShortAnswerEvaluator.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    @staticmethod
    def evaluate(user_answer: str, accepted_answers: list[str]) -> dict:
        """
        Avalia a resposta do utilizador contra a lista de respostas aceites.
        Retorna score (0 ou 100) e feedback.
        """
        user_normalized = ShortAnswerEvaluator.normalize(user_answer)
        
        if not user_normalized:
            return {"score": 0, "is_correct": False, "feedback": "Não escreveste nada. Tenta outra vez!"}
        
        for accepted in accepted_answers:
            accepted_normalized = ShortAnswerEvaluator.normalize(accepted)
            
            # Exact match
            if user_normalized == accepted_normalized:
                return {"score": 100, "is_correct": True, "feedback": "Excelente! Resposta correta! 🎉"}
            
            # Fuzzy match (allow 1-2 typos depending on length)
            max_distance = 1 if len(accepted_normalized) <= 6 else 2
            distance = ShortAnswerEvaluator.levenshtein_distance(user_normalized, accepted_normalized)
            
            if distance <= max_distance:
                return {"score": 100, "is_correct": True, "feedback": f"Boa! Resposta correta (com pequeno erro de escrita). 👍"}
        
        # Wrong answer
        correct_answer = accepted_answers[0] if accepted_answers else "?"
        return {
            "score": 0, 
            "is_correct": False, 
            "feedback": f"Quase! A resposta correta era: **{correct_answer}**. Continua a tentar!",
            "correct_answer": correct_answer
        }

