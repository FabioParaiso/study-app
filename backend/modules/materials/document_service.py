from io import BytesIO
from typing import Protocol
from pypdf import PdfReader


class DocumentExtractor(Protocol):
    def extract(self, file_content: bytes) -> str:
        ...


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
    def __init__(self, extractors: dict[str, DocumentExtractor] | None = None):
        self.extractors = extractors or {
            "application/pdf": PdfTextExtractor(),
            "text/plain": PlainTextExtractor(),
        }
        self.default_extractor = self.extractors.get("text/plain", PlainTextExtractor())

    def extract_text(self, file_content: bytes, file_type: str) -> str:
        """Extracts text from PDF or TXT content."""
        try:
            extractor = self.extractors.get(file_type, self.default_extractor)
            return extractor.extract(file_content)
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
