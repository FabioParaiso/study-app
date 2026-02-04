from modules.quizzes.prompts_base import COMMON_LANGUAGE_RULES, PERSONA_TEACHER

MULTIPLE_CHOICE_TEMPLATE = """
{topic_instruction}

{persona}. Cria um Quiz de escolha múltipla com enunciados curtos e diretos.
NÍVEL: 5º ao 9º ano (11-15 anos).

{priority_instruction}
{vocab_instruction}

OBJETIVO: APRENDER A BRINCAR
O objetivo é ajudar o aluno a perceber os conceitos sem sentir que está num teste aborrecido.

REGRAS DE OURO PARA AS PERGUNTAS (EXEMPLOS):
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
4. NÃO use prefixos de letra ou número (ex: "a)", "b)", "1)") no texto das opções.

CRITÉRIOS DE EXPLICAÇÃO (MODELO MENTAL):
- Explica COMO se chega à resposta correta.
- Começa com "Sabias que..." ou "Imagina que..." sempre que possível.
- Usa ANALOGIAS DO DIA-A-DIA (ex: comparar a célula a uma fábrica ou cidade).
- O tom deve ser positivo, curioso e fácil de ler.
- Mantém a explicação curta: 1-2 frases, até 25 palavras.

{language_rules}

REGRAS DE SAÍDA (JSON ESTRITO) — OBRIGATÓRIO:
- Devolve APENAS JSON válido (sem markdown, sem texto extra).
- Mantém o schema EXACTO e não inventes chaves.
- Se a LISTA FINAL DE CONCEITOS estiver vazia, devolve {{ "questions": [] }}.

VALIDAÇÕES OBRIGATÓRIAS:
- "questions" tem exatamente o nº de linhas da LISTA FINAL DE CONCEITOS.
- Cada "question" termina com "?".
- "concepts" tem 1 item e está na lista fornecida.
- "options" tem 4 itens; "correctIndex" está entre 0 e 3.

AUTO-VERIFICAÇÃO (antes de responder):
- JSON válido + nº de perguntas correto + conceitos dentro da lista.

FORMATO DE SAÍDA (JSON ESTRITO):
Retorna APENAS um objeto JSON com a chave "questions".
{{
    "questions": [
        {{
            "topic": "Nome do Tópico Principal",
            "concepts": ["Nome Exato do Conceito Avaliado (Apenas 1)"],
            "question": "Pergunta interessante?",
            "options": ["Distrator plausível", "Outro distrator", "Opção correta", "Terceiro distrator"],
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
NÍVEL: 5º ao 9º ano (11-15 anos).

{priority_instruction}
{vocab_instruction}

REGRAS (TAXONOMIA DE BLOOM):
Distribui as 5 perguntas assim:
- 2 de COMPREENDER: "Explica por palavras tuas...", "O que significa...?"
- 2 de ANALISAR/APLICAR: "Dá um exemplo prático de...", "Compara..."
- 1 de AVALIAR/CRIAR: "Na tua opinião...", "Como resolverias...?"
Evita perguntas de "sim/não". Cada resposta deve ser explicativa (1-2 frases).
As perguntas devem terminar com "?". Evita repetir o mesmo conceito nas 5 perguntas.

INTEGRAÇÃO DE CONCEITOS (Avançado):
- Tenta criar perguntas que liguem 2 ou mais conceitos, se fizer sentido.
- Exemplo: "Como é que a [Fotossíntese] ajuda na [Respiração Celular]?"

EXEMPLOS DE PERGUNTAS (CALIBRAÇÃO):
❌ MAU (Vago): "Fala-me sobre a fotossíntese." (O aluno não sabe por onde começar)
❌ MAU (Fechado): "A fotossíntese usa luz?" (Responde-se com Sim/Não)
✅ BOM (Equilibrado): "Explica, por palavras tuas, porque é que a fotossíntese é essencial para a vida na Terra."

{language_rules}

REGRAS DE SAÍDA (JSON) — OBRIGATÓRIO:
- Devolve APENAS JSON válido (sem markdown, sem texto extra).
- Mantém o schema EXACTO e não inventes chaves.
- Se a LISTA DE CONCEITOS estiver vazia, devolve {{ "questions": [] }}.

VALIDAÇÕES OBRIGATÓRIAS:
- "questions" tem exatamente 5 perguntas.
- Cada "question" termina com "?".
- "concepts" tem 1-2 itens e só usa conceitos da lista.

AUTO-VERIFICAÇÃO (antes de responder):
- JSON válido + nº de perguntas correto + conceitos dentro da lista.

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

{persona}. Cria um mini-teste de RESPOSTA CURTA (FRASE SIMPLES).
NÍVEL: 5º ao 9º ano (11-15 anos).

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
3. Tamanho da resposta esperada: 5 a 15 palavras (não aceites 1 palavra).
4. A pergunta deve ter no máximo 12-15 palavras, direta e clara.
5. Evita perguntas negativas ou com dupla negação.
6. Evita repetir sempre o mesmo padrão (ex: "O que é...", "Para que serve...").
7. **FOCA-TE NUM ÚNICO CONCEITO POR PERGUNTA.** O campo "concepts" deve ter exatamente 1 conceito da lista.

⚠️ ATENÇÃO CRÍTICA - FORMATO DA PERGUNTA:
- O campo 'question' deve conter uma FRASE INTERROGATIVA (termina com ?).
- NUNCA coloques uma afirmação ou resposta no campo 'question'.
- CORRETO: "Como é o sistema digestivo dos ruminantes?"
- ERRADO: "O estômago tem quatro compartimentos." (Isto é uma afirmação!)

{language_rules}

REGRAS DE SAÍDA (JSON) — OBRIGATÓRIO:
- Devolve APENAS JSON válido (sem markdown, sem texto extra).
- Mantém o schema EXACTO e não inventes chaves.
- Se a LISTA DE CONCEITOS estiver vazia, devolve {{ "questions": [] }}.

VALIDAÇÕES OBRIGATÓRIAS:
- "questions" tem exatamente o nº de linhas da LISTA FINAL DE CONCEITOS.
- Cada "question" termina com "?".
- "concepts" tem exatamente 1 item e corresponde ao conceito dessa linha.
- Se um conceito aparecer mais do que uma vez, cria perguntas DIFERENTES em cada ocorrência.

AUTO-VERIFICAÇÃO (antes de responder):
- JSON válido + nº de perguntas correto + conceitos dentro da lista.

FORMATO DE SAÍDA (JSON):
Gera exatamente o nº de perguntas indicado na lista e não incluas texto fora do JSON.
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

RESUMO DA TAREFA:
- Avalia a resposta e devolve apenas o JSON pedido.
- Não inventes factos fora do texto.

TAREFA:
{extra_instructions}
3. Identifica O QUE FALTOU referir (missing_points).
4. Cria uma RESPOSTA MODELO COMPLETA (model_answer).
5. Cria uma CURIOSIDADE separada quando a nota for < 100.

GUIA DE PONTUAÇÃO:
{scoring_rubric}

{language_rules}

REGRAS DE SAÍDA (JSON) — OBRIGATÓRIO:
- Devolve APENAS JSON válido (sem markdown, sem texto extra).
- Mantém o schema EXACTO e não inventes chaves.

AUTO-VERIFICAÇÃO (antes de responder):
- JSON válido + score entre 0-100 + condições de missing_points/model_answer/curiosity respeitadas.

CRITÉRIOS DE AVALIAÇÃO ESPECÍFICOS:
- SE A NOTA FOR 100: 'missing_points' = [].
- SE A NOTA FOR < 100: 'missing_points' = ["Faltou referir X", "Não disseste Y"].
- SE A NOTA FOR 100 E 'missing_points' = []: 'curiosity' = "".
{model_criteria}

{json_format}
"""
