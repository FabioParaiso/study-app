from modules.common.ports import LLMCallerPort
from services.openai_client import OpenAIClientAdapter
from services.openai_caller import OpenAICaller


def build_openai_caller(api_key: str | None) -> LLMCallerPort:
    if not api_key:
        return OpenAICaller(None)
    client = OpenAIClientAdapter(api_key=api_key)
    return OpenAICaller(client)
