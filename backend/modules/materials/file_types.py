from pathlib import Path


class FileTypeResolver:
    def __init__(self, extension_map: dict[str, str] | None = None, default_type: str = "text/plain"):
        self._extension_map = extension_map or {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
        }
        self._default_type = default_type

    def resolve(self, filename: str, explicit_type: str | None) -> str:
        if explicit_type:
            return explicit_type
        suffix = Path(filename).suffix.lower()
        return self._extension_map.get(suffix, self._default_type)
