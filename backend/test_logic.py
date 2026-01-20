import pytest
from unittest.mock import MagicMock, patch
from services.document_service import DocumentService
from services.ai_service import AIService

class MockUploadedFile:
    def __init__(self, content, file_type):
        self.content = content
        self.type = file_type

    def getvalue(self):
        return self.content

def test_extract_text_txt():
    content = b"Ola mundo"
    # DocumentService.extract_text expects bytes for content (from UploadFile.read())
    # but the service handles decoding.
    # The original test mocked UploadFile, but DocumentService now takes bytes + type
    text = DocumentService.extract_text(content, "text/plain")
    assert text == "Ola mundo"

@patch('services.ai_service.OpenAI')
def test_generate_quiz_success(mock_openai):
    # Mock the API response
    mock_client = MagicMock()
    mock_response = MagicMock()
    # OpenAI response structure
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '''
    {
        "questions": [
            {
                "question": "Questao 1",
                "options": ["A", "B", "C", "D"],
                "correctIndex": 0,
                "explanation": "Porque sim."
            }
        ]
    }
    '''
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    service = AIService("fake_key")
    quiz = service.generate_quiz("Texto de teste")

    assert len(quiz) == 1
    assert quiz[0]['question'] == "Questao 1"
    assert quiz[0]['correctIndex'] == 0

def test_generate_quiz_no_key():
    service = AIService(None)
    quiz = service.generate_quiz("Texto")
    assert quiz is None
