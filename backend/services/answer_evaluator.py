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
