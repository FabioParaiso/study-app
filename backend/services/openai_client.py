from openai import OpenAI
from modules.common.ports import OpenAIClientPort


class OpenAIClientAdapter(OpenAIClientPort):
    def __init__(self, api_key: str):
        self._client = OpenAI(api_key=api_key)

    def chat_completions_create(self, **kwargs):
        return self._client.chat.completions.create(**kwargs)
