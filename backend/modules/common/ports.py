from typing import Protocol, TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class TokenServicePort(Protocol):
    def create_access_token(self, data: dict) -> str: ...
    def decode_access_token(self, token: str) -> dict | None: ...


class OpenAIClientPort(Protocol):
    def chat_completions_create(self, **kwargs: Any) -> Any: ...
