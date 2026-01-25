from abc import ABC, abstractmethod
import json
from modules.quizzes.prompts_base import COMMON_LANGUAGE_RULES, PERSONA_TEACHER

# --- Prompt Builders (single source of truth) ---
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

def _build_priority_instruction(priority_topics: list[str], min_questions: int = 2) -> str:
    if not priority_topics:
        return ""
    p_str = ", ".join(priority_topics)
    return f"\nATENÇÃO: O aluno tem DIFICULDADE nos seguintes tópicos: {p_str}. Cria pelo menos {min_questions} perguntas focadas neles para reforço."

def _build_vocab_instruction(material_concepts: list[str]) -> str:
    if not material_concepts:
        return ""
    v_str = ", ".join(material_concepts)
    return f"""BASE DE CONCEITOS ACEITES (WHITELIST):
    Ao criar perguntas, tens de escolher o 'alvo' DA LISTA ABAIXO.
    [{v_str}]
    - NÃO inventes conceitos novos. Usa apenas estes termos aprovados.
    - Se o utilizador pediu um Tópico Específico, escolhe desta lista os conceitos que pertencem a esse tópico."""

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

def _get_evaluation_json_format() -> str:
    return """SAÍDA (JSON):
        { 
            "score": 0-100,
            "feedback": "Frase motivacional curta (5-10 palavras).",
            "missing_points": ["Ponto curto 1", "Ponto curto 2"],
            "model_answer": "Resposta simples em 2-3 frases curtas. Máximo 50 palavras!",
            "curiosity": "Sabias que [facto curto]?"
        }"""

def _build_evaluation_context(text: str, question: str, user_answer: str) -> str:
    return f"""CONTEXTO (Matéria):
        {text[:30000]}...

        PERGUNTA: "{question}"
        RESPOSTA DO ALUNO: "{user_answer}\""""

def get_multiple_choice_prompt(text: str, topics: list[str], priority_topics: list[str], material_concepts: list[str]) -> str:
    topic_instr = _build_topic_instruction(topics, material_concepts)
    priority_instr = _build_priority_instruction(priority_topics, min_questions=4)
    vocab_instr = _build_vocab_instruction(material_concepts)

    return f"""
        {topic_instr}

        {PERSONA_TEACHER}. Cria um Quiz de 10 perguntas de escolha múltipla SIMPLES.

        {priority_instr}
        {vocab_instr}

        OBJETIVO: APRENDER A BRINCAR
        O objetivo é ajudar o aluno a perceber os conceitos sem sentir que está num teste aborrecido.
        
        REGRAS DE OURO PARA AS PERGUNTAS (FEW-SHOT):
        1. Foca-te na COMPREENSÃO, não na memorização.
           ❌ MAU: "Em que ano foi assinada a independência?" (Memorização seca)
           ✅ BOM: "Porque é que a independência foi importante para o povo?" (Compreensão)
        2. Usa situações práticas sempre que possível.
           ✅ BOM: "Se deixares uma planta no escuro, o que lhe acontece?"

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

        {COMMON_LANGUAGE_RULES}
        - ESCRITA COMO SE FOSSES UM YOUTUBER A EXPLICAR ALGO FIXE.

        FORMATO DE SAÍDA (JSON ESTRITO):
        Retorna APENAS um objeto JSON com a chave "questions".
        {{
            "questions": [
                {{
                    "topic": "Tópico Específico",
                    "question": "Pergunta interessante?",
                    "options": ["Opção Plausível A", "Opção Plausível B", "Opção Correta", "Opção Plausível C"],
                    "correctIndex": 2,
                    "explanation": "Sabias que... [Explicação divertida com analogia ou curiosidade]"
                }}
            ]
        }}

        TEXTO DE ESTUDO:
        {text[:50000]}
        """

def get_open_ended_prompt(text: str, topics: list[str], priority_topics: list[str], material_concepts: list[str]) -> str:
    topic_instr = _build_topic_instruction(topics, material_concepts)
    priority_instr = _build_priority_instruction(priority_topics, min_questions=1)
    vocab_instr = _build_vocab_instruction(material_concepts)

    return f"""
        {topic_instr}

        {PERSONA_TEACHER}. Cria um mini-teste de 5 perguntas de resposta aberta.

        {priority_instr}
        {vocab_instr}

        REGRAS (TAXONOMIA DE BLOOM):
        Distribui as 5 perguntas assim:
        - 2 de COMPREENDER: "Explica por palavras tuas...", "O que significa...?"
        - 2 de ANALISAR/APLICAR: "Dá um exemplo prático de...", "Compara..."
        - 1 de AVALIAR/CRIAR: "Na tua opinião...", "Como resolverias...?"
        Evita perguntas de "sim/não". Cada resposta deve ser explicativa (1-2 frases).

        EXEMPLOS DE PERGUNTAS (CALIBRAÇÃO):
        ❌ MAU (Vago): "Fala-me sobre a fotossíntese." (O aluno não sabe por onde começar)
        ❌ MAU (Fechado): "A fotossíntese usa luz?" (Responde-se com Sim/Não)
        ✅ BOM (Equilibrado): "Explica, por palavras tuas, porque é que a fotossíntese é essencial para a vida na Terra."

        {COMMON_LANGUAGE_RULES}

        FORMATO DE SAÍDA (JSON):
        {{ 
            "questions": [
                {{ "topic": "Tema", "question": "Questão..." }}
            ] 
        }}

        TEXTO:
        {text[:50000]}
        """

def get_short_answer_prompt(text: str, topics: list[str], priority_topics: list[str], material_concepts: list[str]) -> str:
    topic_instr = _build_topic_instruction(topics, material_concepts)
    priority_instr = _build_priority_instruction(priority_topics, min_questions=2)
    vocab_instr = _build_vocab_instruction(material_concepts)

    return f"""
        {topic_instr}

        {PERSONA_TEACHER}. Cria um mini-teste de 8 perguntas de RESPOSTA CURTA (FRASE SIMPLES).

        {priority_instr}
        {vocab_instr}

        OBJETIVO: TREINO DE SINTAXE E FACTOS
        O objetivo deste nível (Intermédio) é garantir que o aluno sabe construir uma frase completa com Sujeito e Verbo. Não queremos ainda reflexões profundas.

        REGRAS DE CRIAÇÃO (SINTAXE vs CONTEÚDO):
        1. Foca-te em FACTOS CONCRETOS (O quê, Quem, Onde, Como).
           ❌ PROIBIDO: Perguntas de "Porquê" complexo ou "Opinião" (Isso é para o Nível Avançado).
        2. A resposta ideal deve ter SUJEITO e VERBO explícitos.
           ❌ MAU: "Qual o nome do processo?" (Resposta: "Fotossíntese" -> 1 palavra, Errado para este nível)
           ✅ BOM: "O que fazem as plantas na fotossíntese?" (Resposta: "As plantas produzem o seu alimento.")
        3. Tamanho da resposta esperada: 5 a 15 palavras.

        ⚠️ ATENÇÃO CRÍTICA - FORMATO DA PERGUNTA:
        - O campo 'question' deve conter uma FRASE INTERROGATIVA (termina com ?).
        - NUNCA coloques uma afirmação ou resposta no campo 'question'.
        - CORRETO: "Como é o sistema digestivo dos ruminantes?"
        - ERRADO: "O estômago tem quatro compartimentos." (Isto é uma afirmação!)

        {COMMON_LANGUAGE_RULES}

        FORMATO DE SAÍDA (JSON):
        {{ 
            "questions": [
                {{ 
                    "topic": "Tema",
                    "question": "Pergunta que exige frase simples? (DEVE TERMINAR COM ?)"
                }}
            ] 
        }}

        TEXTO:
        {text[:50000]}
        """

def get_evaluation_prompt(text: str, question: str, user_answer: str, quiz_type: str = "open-ended") -> str:
    context = _build_evaluation_context(text, question, user_answer)
    model_criteria = _get_model_answer_criteria()
    json_format = _get_evaluation_json_format()

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

    return f"""
        {PERSONA_TEACHER}.
        O teu objetivo é AJUDAR o aluno a aprender, não apenas avaliar.
        
        {context}

        TAREFA:
        {extra_instructions}
        3. Identifica O QUE FALTOU referir (missing_points).
        4. Cria uma RESPOSTA MODELO COMPLETA (model_answer).
        5. Cria uma CURIOSIDADE separada.

        {COMMON_LANGUAGE_RULES}

        CRITÉRIOS DE AVALIAÇÃO ESPECÍFICOS:
        - SE A NOTA FOR 100: 'missing_points' = [].
        - SE A NOTA FOR < 100: 'missing_points' = ["Faltou referir X", "Não disseste Y"].
        {model_criteria}

        {json_format}
        """

class QuizGenerationStrategy(ABC):
    """
    Classe base abstrata para estratégias de geração de quizzes.
    Contém métodos auxiliares partilhados para construir instruções dinâmicas.
    """
    # Helper methods removed in favor of centralized prompt module

    @abstractmethod
    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_concepts: list[str] = None) -> str:
        pass

    def parse_response(self, response_content: str) -> list[dict]:
        """Implementação padrão de parsing JSON."""
        try:
            data = json.loads(response_content)
            return data.get("questions", [])
        except json.JSONDecodeError:
            return []


class MultipleChoiceStrategy(QuizGenerationStrategy):
    """
    Modo Iniciante: Perguntas de escolha múltipla.
    Foco na compreensão de conceitos com feedback explicativo.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_concepts: list[str] = None) -> str:
        return get_multiple_choice_prompt(text, topics, priority_topics, material_concepts)


class OpenEndedStrategy(QuizGenerationStrategy):
    """
    Modo Avançado: Perguntas de resposta aberta.
    Exige pensamento crítico seguindo a Taxonomia de Bloom.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_concepts: list[str] = None) -> str:
        return get_open_ended_prompt(text, topics, priority_topics, material_concepts)

    def generate_evaluation_prompt(self, text: str, question: str, user_answer: str) -> str:
        return get_evaluation_prompt(text, question, user_answer, quiz_type="open-ended")


class ShortAnswerStrategy(QuizGenerationStrategy):
    """
    Modo Intermédio: Perguntas de resposta curta (Frase simples).
    Exige construção de frase, mas sem a complexidade de um texto longo.
    """

    def generate_prompt(self, text: str, topics: list[str], priority_topics: list[str] = None, material_concepts: list[str] = None) -> str:
        return get_short_answer_prompt(text, topics, priority_topics, material_concepts)

    def generate_evaluation_prompt(self, text: str, question: str, user_answer: str) -> str:
        # Reusing the unified evaluation prompt with type hint
        return get_evaluation_prompt(text, question, user_answer, quiz_type="short_answer")
