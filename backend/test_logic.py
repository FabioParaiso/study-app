import pytest
from unittest.mock import MagicMock, patch
from logic import extract_text_from_file, generate_quiz

class MockUploadedFile:
    def __init__(self, content, file_type):
        self.content = content
        self.type = file_type

    def getvalue(self):
        return self.content

def test_extract_text_txt():
    content = b"Ola mundo"
    file = MockUploadedFile(content, "text/plain")
    text = extract_text_from_file(file)
    assert text == "Ola mundo"

@patch('logic.genai')
def test_generate_quiz_success(mock_genai):
    # Mock the API response
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '''
    [
        {
            "pergunta": "Questao 1",
            "opcoes": ["A", "B", "C", "D"],
            "resposta_correta": 0,
            "explicacao": "Porque sim."
        }
    ]
    '''
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    quiz = generate_quiz("Texto de teste", "fake_key")

    assert len(quiz) == 1
    assert quiz[0]['pergunta'] == "Questao 1"
    assert quiz[0]['resposta_correta'] == 0

def test_generate_quiz_no_key():
    quiz = generate_quiz("Texto", None)
    assert quiz is None
