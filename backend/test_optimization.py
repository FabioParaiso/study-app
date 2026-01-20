import pytest
from unittest.mock import MagicMock, patch
from services.document_service import DocumentService

class MockUploadedFile:
    def __init__(self, content, file_type):
        self.content = content
        self.type = file_type

    def getvalue(self):
        return self.content

@patch('services.document_service.PdfReader')
def test_extract_text_pdf_optimized(mock_pdf_reader):
    """
    Verify that PDF text extraction correctly joins text from multiple pages.
    This tests the optimization (list accumulation vs string concatenation).
    """
    # Setup mock pages
    page1 = MagicMock()
    page1.extract_text.return_value = "Page 1 content. "
    page2 = MagicMock()
    page2.extract_text.return_value = "Page 2 content."

    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [page1, page2]
    mock_pdf_reader.return_value = mock_reader_instance

    # DocumentService.extract_text takes bytes
    text = DocumentService.extract_text(b"fake pdf content", "application/pdf")

    assert text == "Page 1 content. Page 2 content."
    # Verify we actually called extract_text
    page1.extract_text.assert_called_once()
    page2.extract_text.assert_called_once()
