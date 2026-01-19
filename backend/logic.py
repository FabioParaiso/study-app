import json
from openai import OpenAI
from pypdf import PdfReader

def extract_text_from_file(uploaded_file):
    """Extracts text from PDF or TXT files."""
    try:
        # Check if it's a Streamlit UploadedFile or just bytes/string IO
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            return "".join(text_parts)
        else:
            # Assume text/plain
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        print(f"Erro ao ler o ficheiro: {e}")
        return None

def generate_quiz(text, api_key, topics=None):
    """Generates a quiz using OpenAI API."""
    if not api_key:
        return None

    try:
        client = OpenAI(api_key=api_key)
        
        topic_instruction = ""
        if topics and len(topics) > 0:
            topic_list = ", ".join(topics)
            topic_instruction = f"\n        Foca o questionário EXCLUSIVAMENTE nos seguintes tópicos: {topic_list}.\n"

        prompt = f"""
        És um professor experiente e encorajador do 6º ano de escolaridade em Portugal.
        Lê o seguinte texto de estudo e cria um questionário com 10 perguntas de escolha múltipla.
        {topic_instruction}
        O questionário deve testar a compreensão da matéria.
        A linguagem deve ser adequada a uma criança de 12 anos (Português de Portugal - PT-PT).
        
        CRITÉRIOS ESTRITOS DE LINGUAGEM (PT-PT):
        1. Usa "Tu" ou constrói frases de forma impessoal. NUNCA uses "Você".
        2. Vocabulário: Usa "Ecrã" (não tela), "Rato" (não mouse), "Ficheiro" (não arquivo), "Guardar" (não salvar), "Equipa" (não time), "Desporto" (não esporte), "Facto" (não fato).
        3. Gerúndio: Usa "A fazer", "A correr" (NUNCA "fazendo", "correndo").
        
        Retorna APENAS um JSON válido. Não uses blocos de código markdown (```json).
        O formato deve ser uma lista de objetos com a seguinte estrutura:
        [
            {{
                "question": "A pergunta aqui?",
                "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
                "correctIndex": 0,  // Índice da resposta correta (0 a 3) inteiro
                "explanation": "Uma breve explicação de porque está correta, num tom encorajador."
            }}
        ]

        Texto de Estudo:
        {text[:10000]}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates JSON. Always return just the JSON array."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        content = response.choices[0].message.content
        
        print(f"DEBUG - OpenAI Response Content: {content}") # Debugging line
        
        data = json.loads(content)
        
        # Helper to extract list if wrapped
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
             # Try to find a list value commonly named 'questions' or 'quiz' or just the first list found
             if 'questions' in data and isinstance(data['questions'], list):
                 return data['questions']
             if 'quiz' in data and isinstance(data['quiz'], list):
                 return data['quiz']
             
             for key, value in data.items():
                 if isinstance(value, list):
                     return value
        
        return None
        
    except Exception as e:
        print(f"Ocorreu um erro ao gerar o questionário (OpenAI): {e}")
        return None

import re

def extract_topics(text, api_key=None): # api_key arg kept for signature compatibility
    """
    Extracts high-level topics/headers using hierarchical heuristics (Regex).
    Priority: H1 > H2 > H3. Returns the highest level found.
    """
    # Regex Priorities
    # H1: "1. Title", "I. Title", "Chapter 1", "Capítulo 1"
    h1_regex = re.compile(r'^(?:(?:\d+\.)|[IVX]+\.?|Chapter\s+\d+|Capítulo\s+\d+|Módulo\s+\d+)\s+([A-Z].{2,})', re.IGNORECASE)
    
    # H2: "1.1 Title", "1.1. Title", "A) Title"
    h2_regex = re.compile(r'^(?:(?:\d+\.\d+\.?)|[A-Z]\))\s+([A-Z].{2,})', re.IGNORECASE)
    
    # H3: "1.1.1 Title", "a) Title"
    h3_regex = re.compile(r'^(?:(?:\d+\.\d+\.\d+\.?)|[a-z]\))\s+([A-Z].{2,})', re.IGNORECASE)

    # Fallback: Loose Title Detection (No numbers, just capital start, no end dot)
    # Excludes lines starting with bullets (●, -, •) unless they look really like headers
    loose_title_regex = re.compile(r'^(?![•●-])([A-ZÀ-Ú][^.!?]{3,120})$') 

    found_h1 = []
    found_h2 = []
    found_h3 = []
    found_loose = []

    # Optimization: Combined cleaning and matching in single pass
    for line in text.splitlines():
        # Clean lines & Normalize spaces using string methods (fastest for this case)
        norm_line = " ".join(line.split())

        if not norm_line or len(norm_line) >= 150:
            continue

        # Match H1
        m1 = h1_regex.match(norm_line)
        if m1:
            found_h1.append(norm_line)
            continue 

        # Match H2
        m2 = h2_regex.match(norm_line)
        if m2:
            found_h2.append(norm_line)
            continue

        # Match H3
        m3 = h3_regex.match(norm_line)
        if m3:
            found_h3.append(norm_line)
            continue

        # Match Loose Title (Fallback)
        if loose_title_regex.match(norm_line):
             # Heuristic: Title usually doesn't have "page"
             if "página" not in norm_line.lower() and "page" not in norm_line.lower():
                found_loose.append(norm_line)

    # Priority Return Rule: "O maior que existir"
    def dedup(lst):
        # Optimization: Use dict.fromkeys for faster deduplication while preserving order
        return list(dict.fromkeys(lst))

    if found_h1:
        return dedup(found_h1)[:20]
    
    if found_h2:
        return dedup(found_h2)[:20]

    if found_h3:
        return dedup(found_h3)[:20]
        
    # If no strict headers found, return the loose titles (e.g. "Mamíferos omnívoros")
    if found_loose:
        return dedup(found_loose)[:25]

    # Absolute fallback
    return ["Tópicos Gerais"]

def generate_open_questions(text, api_key, topics=None):
    """Generates 5 open-ended questions."""
    if not api_key:
        return None

    try:
        client = OpenAI(api_key=api_key)
        
        topic_instruction = ""
        if topics and len(topics) > 0:
            topic_str = ", ".join(topics)
            topic_instruction = f"Foca as perguntas nestes tópicos: {topic_str}."

        prompt = f"""
        És um professor experiente. Lê o texto e cria um teste de 5 perguntas de resposta aberta (pequeno desenvolvimento).
        
        {topic_instruction}
        
        REGRAS:
        1. Cria EXATAMENTE 5 perguntas.
        2. As perguntas devem ser ABERTAS (exigem explicação), mas SIMPLES e FOCADAS.
        3. Cada pergunta deve focar num único conceito.
        4. Linguagem adequada a uma criança de 12 anos (Português de Portugal - PT-PT).
        
        CRITÉRIOS ESTRITOS DE LINGUAGEM (PT-PT):
        1. Usa "Tu" ou constrói frases de forma impessoal. NUNCA uses "Você".
        2. Vocabulário: Usa "Ecrã" (não tela), "Rato" (não mouse), "Ficheiro" (não arquivo), "Guardar" (não salvar), "Equipa" (não time), "Desporto" (não esporte), "Facto" (não fato).
        3. Gerúndio: Usa "A fazer", "A correr" (NUNCA "fazendo", "correndo").
        
        Retorna APENAS um JSON válido com esta estrutura:
        {{ 
            "questions": [
                {{ "topic": "Tema", "question": "Texto da pergunta..." }}
            ] 
        }}

        Texto:
        {text[:10000]}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant found in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("questions", [])

    except Exception as e:
        print(f"Error generating open questions: {e}")
        return None

def evaluate_answer(text, question, user_answer, api_key):
    """Evaluates a user's answer to an open-ended question."""
    if not api_key:
        return None

    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        És um professor.
        Contexto (Matéria):  {text[:5000]}...
        
        Pergunta: "{question}"
        Resposta do aluno: "{user_answer}"
        
        Avalia a resposta numa escala de 0 a 100.
        Dá um feedback curto (max 2 frases) e pedagógico em Português de Portugal (PT-PT).
        Usa "Tu" ou impessoal (NUNCA "Você"). Usa "A fazer" em vez de "Fazendo".
        Se estiver errada, explica o correto.
        
        Retorna JSON: {{ "score": number, "feedback": "string" }}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a teacher evaluating answers. Return JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return {"score": 0, "feedback": "Erro ao avaliar. Tenta novamente."}
