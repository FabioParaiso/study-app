class AnswerEvaluator:
    @staticmethod
    def generate_prompt(strategy, text: str, question: str, user_answer: str) -> str:
        """
        Gera o prompt de avaliação usando a estratégia fornecida.
        """
        if hasattr(strategy, "generate_evaluation_prompt"):
            return strategy.generate_evaluation_prompt(text, question, user_answer)
        
        # Fallback (caso a estratégia não tenha avaliação, ex: escolha múltipla)
        return "Erro: Estratégia não suporta avaliação de resposta aberta/curta."
