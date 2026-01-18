import json
from openai import OpenAI
from pypdf import PdfReader

def extract_text_from_file(uploaded_file):
    """Extracts text from PDF or TXT files."""
    try:
        # Check if it's a Streamlit UploadedFile or just bytes/string IO
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            # ⚡ Bolt Optimization: Use list join instead of string concatenation
            pages_text = []
            for page in reader.pages:
                pages_text.append(page.extract_text())
            return "".join(pages_text)
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

        Retorna APENAS um JSON válido. Não uses blocos de código markdown (```json).
        O formato deve ser uma lista de objetos com a seguinte estrutura:
        [
            {{
                "pergunta": "A pergunta aqui?",
                "opcoes": ["Opção A", "Opção B", "Opção C", "Opção D"],
                "resposta_correta": 0,  // Índice da resposta correta (0 a 3) inteiro
                "explicacao": "Uma breve explicação de porque está correta, num tom encorajador."
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

def extract_topics(text, api_key):
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        Analisa o seguinte texto de estudo e identifica os 5 principais tópicos, capítulos ou conceitos abordados.
        Retorna APENAS um array JSON de strings.
        Exemplo: ["Ciclo da Água", "Tipos de Nuvens", "Precipitação"]

        Texto (primeiras 5000 palavras):
        {text[:15000]}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts topics. Return only JSON array."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        if "topics" in data:
            return data["topics"]
        elif "topicos" in data:
             return data["topicos"]
        elif isinstance(data, list):
            return data
        
        # Fallback
        for key, value in data.items():
            if isinstance(value, list):
                return value
                
        return []

    except Exception as e:
        print(f"Error extracting topics: {e}")
        # Default topic if extraction fails
        return ["Geral"]
