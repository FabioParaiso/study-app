import pytest
import asyncio
from unittest.mock import MagicMock, patch
from services.document_service import DocumentService

# This test file ensures that CPU-bound tasks in DocumentService can be safely offloaded to threads
# to prevent blocking the main asyncio event loop in FastAPI routers.

@patch('services.document_service.PdfReader')
@pytest.mark.asyncio
async def test_extract_text_pdf_in_thread(mock_pdf_reader):
    """
    Verify that PDF text extraction works correctly when offloaded to a thread.
    This ensures the service method is thread-safe (stateless) and compatible with asyncio.to_thread.
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
    # Run in thread using the same mechanism as the router
    text = await asyncio.to_thread(DocumentService.extract_text, b"fake pdf content", "application/pdf")

    assert text == "Page 1 content. Page 2 content."
    # Verify we actually called extract_text
    page1.extract_text.assert_called_once()
    page2.extract_text.assert_called_once()
