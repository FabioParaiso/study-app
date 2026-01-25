from modules.quizzes.prompts_base import COMMON_LANGUAGE_RULES, PERSONA_TEACHER

MULTIPLE_CHOICE_TEMPLATE = """
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
3. **FOCA-TE NUM ÚNICO CONCEITO POR PERGUNTA.**

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
            "topic": "Nome do Tópico Principal",
            "concepts": ["Nome Exato do Conceito Avaliado (Apenas 1)"],
            "question": "Pergunta interessante?",
            "options": ["Opção Plausível A", "Opção Plausível B", "Opção Correta", "Opção Plausível C"],
            "correctIndex": 2,
            "explanation": "Sabias que... [Explicação divertida com analogia ou curiosidade]"
        }}
    ]
}}

TEXTO DE ESTUDO:
{text}
"""

OPEN_ENDED_TEMPLATE = """
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

INTEGRAÇÃO DE CONCEITOS (Avançado):
- Tenta criar perguntas que liguem 2 ou mais conceitos, se fizer sentido.
- Exemplo: "Como é que a [Fotossíntese] ajuda na [Respiração Celular]?"

EXEMPLOS DE PERGUNTAS (CALIBRAÇÃO):
❌ MAU (Vago): "Fala-me sobre a fotossíntese." (O aluno não sabe por onde começar)
❌ MAU (Fechado): "A fotossíntese usa luz?" (Responde-se com Sim/Não)
✅ BOM (Equilibrado): "Explica, por palavras tuas, porque é que a fotossíntese é essencial para a vida na Terra."

{language_rules}

FORMATO DE SAÍDA (JSON):
{{ 
    "questions": [
        {{ 
            "topic": "Tema Principal", 
            "concepts": ["Conceito A", "Conceito B (Opcional)"],
            "question": "Questão..." 
        }}
    ] 
}}

TEXTO:
{text}
"""

SHORT_ANSWER_TEMPLATE = """
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
4. **FOCA-TE NUM ÚNICO CONCEITO POR PERGUNTA.**

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
            "concepts": ["Conceito Único"],
            "question": "Pergunta que exige frase simples? (DEVE TERMINAR COM ?)"
        }}
    ] 
}}

TEXTO:
{text}
"""

EVALUATION_TEMPLATE = """
{persona}.
O teu objetivo é AJUDAR o aluno a aprender, não apenas avaliar.

{context}

TAREFA:
{extra_instructions}
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
