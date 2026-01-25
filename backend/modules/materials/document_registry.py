from typing import Protocol


class DocumentExtractor(Protocol):
    def extract(self, file_content: bytes) -> str: ...


class DocumentTypeRegistry:
    def __init__(self, extractors: dict[str, DocumentExtractor], default_type: str = "text/plain"):
        self._extractors = dict(extractors)
        self._default_type = default_type

    def register(self, mime_type: str, extractor: DocumentExtractor) -> None:
        self._extractors[mime_type] = extractor

    def get(self, mime_type: str) -> DocumentExtractor:
        return self._extractors.get(mime_type, self._extractors[self._default_type])

    def default_type(self) -> str:
        return self._default_type
