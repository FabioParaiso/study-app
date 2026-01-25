from io import BytesIO
from pypdf import PdfReader
from modules.materials.document_registry import DocumentTypeRegistry


class PdfTextExtractor:
    def extract(self, file_content: bytes) -> str:
        reader = PdfReader(BytesIO(file_content))
        text_parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "".join(text_parts)


class PlainTextExtractor:
    def extract(self, file_content: bytes) -> str:
        return file_content.decode("utf-8")

class DocumentService:
    def __init__(self, registry: DocumentTypeRegistry | None = None):
        self.registry = registry or DocumentTypeRegistry(
            {
                "application/pdf": PdfTextExtractor(),
                "text/plain": PlainTextExtractor(),
            }
        )

    def extract_text(self, file_content: bytes, file_type: str) -> str | None:
        """Extracts text from PDF or TXT content."""
        try:
            extractor = self.registry.get(file_type)
            return extractor.extract(file_content)
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
