class TopicExtractor:
    @staticmethod
    def generate_prompt(text: str, existing_topics: list[str]) -> str:
        existing_topics_str = ", ".join(existing_topics) if existing_topics else "Nenhum"
        
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
        
        TEXTO PARA ANÁLISE:
        {text[:15000]}...

        SAÍDA (JSON):
        {{ "topics": ["Tópico A", "Tópico B"] }}
        """

    @staticmethod
    def parse_response(content: dict) -> list[str]:
        return content.get("topics", [])
