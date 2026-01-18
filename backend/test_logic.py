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

@patch('logic.PdfReader')
def test_extract_text_pdf(mock_pdf_reader):
    # Mock the PdfReader instance
    mock_reader_instance = MagicMock()

    # Mock pages
    page1 = MagicMock()
    page1.extract_text.return_value = "Page 1 content. "
    page2 = MagicMock()
    page2.extract_text.return_value = "Page 2 content."

    mock_reader_instance.pages = [page1, page2]
    mock_pdf_reader.return_value = mock_reader_instance

    file = MockUploadedFile(b"fake pdf content", "application/pdf")
    text = extract_text_from_file(file)

    assert text == "Page 1 content. Page 2 content."

@patch('logic.OpenAI')
def test_generate_quiz_success(mock_openai):
    # Mock the API response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '''
    [
        {
            "pergunta": "Questao 1",
            "opcoes": ["A", "B", "C", "D"],
            "resposta_correta": 0,
            "explicacao": "Porque sim."
        }
    ]
    '''
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    quiz = generate_quiz("Texto de teste", "fake_key")

    assert len(quiz) == 1
    assert quiz[0]['pergunta'] == "Questao 1"
    assert quiz[0]['resposta_correta'] == 0

def test_generate_quiz_no_key():
    quiz = generate_quiz("Texto", None)
    assert quiz is None
