"""
Prompts for Topic and Concept Extraction.
"""

def get_topic_extraction_prompt(text: str, existing_topics: list[str] = None) -> str:
    # Existing topics ignored to ensure strict single-pass isolation

    return f"""
        És um extrator de conhecimento a partir de um ÚNICO texto.
        Objetivo: produzir 3–6 tópicos principais e, por tópico, 3–6 conceitos nucleares e testáveis.

        REGRAS OBRIGATÓRIAS:
        - Lê o texto como um todo; NÃO assumes que é um excerto.
        - Output estritamente no formato JSON pedido.
        - PT-PT; termos técnicos apenas se existirem no texto.
        
        REGRAS DE NOMEAÇÃO (CONCEITOS):
        - O campo conceito deve ter 2–6 palavras, ser um rótulo nominal.
        - NÃO pode conter: "como", "entre", "diferenças", "consome", "liberta", exemplos (ex: "gripe/asma"), nem parênteses.
        - Exemplos e detalhes fisiológicos devem ir para evidências/notas mentais, NUNCA no nome do conceito.
        - Se uma frase for "X como Y...", o conceito é X e o resto é descartado do nome.
        
        TRUQUES PARA QUALIDADE:
        - Restrições: se um conceito for apenas exemplo/detalhe de outro, elimina-o e mantém só o conceito mais abrangente.
        - Heurística: escolhe conceitos que apareçam repetidamente, sejam definidos ou sejam pré-requisitos para outros.

        PROCESSO DE PENSAMENTO (CoT) - Executa internamente:
        1) Inventário: lista mentalmente todos os candidatos a tópicos e conceitos.
        2) Agrupamento: agrupa candidatos em macro-temas coerentes.
        3) Compressão: escolhe 3–6 tópicos e 3–6 conceitos por tópico maximizando cobertura e minimizando redundância.
        4) Verificação: confirma que cada conceito está suportado por evidência no texto.
        5) Se o texto for gigante, prioriza títulos, definições e secções introdutórias.

        FORMATO DE SAÍDA (APENAS JSON)
        {{
            "_raciocinio": "Resumo do inventário e agrupamento, incluindo as evidências (citações) usadas para validar a escolha dos tópicos...",
            "topics": ["Tópico A", "Tópico B", "Tópico C"],
            "concepts_map": {{
                "Tópico A": ["Conceito 1", "Conceito 2"],
                "Tópico B": ["Conceito 3"],
                "Tópico C": []
            }}
        }}

        TEXTO:
        <<<
        {text}
        >>>
        """
