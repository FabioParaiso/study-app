from pypdf import PdfReader
from io import BytesIO

class DocumentService:
    @staticmethod
    def extract_text(file_content: bytes, file_type: str) -> str:
        """Extracts text from PDF or TXT content."""
        try:
            if file_type == "application/pdf":
                reader = PdfReader(BytesIO(file_content))
                text_parts = []
                for page in reader.pages:
                    text_parts.append(page.extract_text())
                return "".join(text_parts)
            else:
                # Assume text/plain
                return file_content.decode("utf-8")
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
