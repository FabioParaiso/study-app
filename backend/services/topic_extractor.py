class TopicExtractor:
    @staticmethod
    def generate_prompt(text: str, existing_topics: list[str]) -> str:
        # Limit existing topics to avoid huge prompts
        safe_topics = existing_topics[:30] if existing_topics else []
        existing_topics_str = ", ".join(safe_topics) if safe_topics else "Nenhum"
        
        return f"""
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
        
        LINGUAGEM (PT-PT OBRIGATÓRIA):
        - Usa APENAS Português de Portugal.
        - Ex: "Desporto" (não Esporte), "Ecrã" (não Tela), "Ficheiro" (não Arquivo), "Equipa" (não Time).
        
        TEXTO PARA ANÁLISE:
        {text[:5000]}...

        SAÍDA (JSON):
        {{ "topics": ["Tópico A", "Tópico B"] }}
        """

    @staticmethod
    def parse_response(content: dict) -> list[str]:
        return content.get("topics", [])
