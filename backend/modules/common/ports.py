from typing import Protocol, TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class TokenServicePort(Protocol):
    def create_access_token(self, data: dict) -> str: ...
    def decode_access_token(self, token: str) -> dict | None: ...


class OpenAIClientPort(Protocol):
    def chat_completions_create(self, **kwargs: Any) -> Any: ...


class LLMCallerPort(Protocol):
    def call(
        self,
        prompt: str,
        system_message: str,
        model: str,
        temperature: float = 0.7,
        seed: int | None = None,
        reasoning_effort: str | None = None
    ) -> str | None: ...
    def is_available(self) -> bool: ...
