import json
import google.generativeai as genai
from pypdf import PdfReader

def extract_text_from_file(uploaded_file):
    """Extracts text from PDF or TXT files."""
    try:
        # Check if it's a Streamlit UploadedFile or just bytes/string IO
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        else:
            # Assume text/plain
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        print(f"Erro ao ler o ficheiro: {e}")
        return None

def generate_quiz(text, api_key):
    """Generates a quiz using Gemini API."""
    if not api_key:
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    És um professor experiente e encorajador do 6º ano de escolaridade em Portugal.
    Lê o seguinte texto de estudo e cria um questionário com 5 perguntas de escolha múltipla.

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

    try:
        response = model.generate_content(prompt)
        content = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except Exception as e:
        print(f"Ocorreu um erro ao gerar o questionário: {e}")
        return None
