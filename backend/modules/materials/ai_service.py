import json
from modules.materials.topic_extractor import TopicExtractor
from services.openai_client import OpenAIClientAdapter
from services.openai_caller import OpenAICaller
from services.ports import OpenAIClientPort


class TopicAIService:
    MODEL_TOPIC_EXTRACTION = "gpt-4o-mini"

    def __init__(self, api_key: str, client: OpenAIClientPort | None = None, caller: OpenAICaller | None = None):
        if caller:
            self.client = caller.client
            self.caller = caller
        else:
            if client:
                self.client = client
            elif api_key:
                self.client = OpenAIClientAdapter(api_key=api_key)
            else:
                self.client = None
            self.caller = OpenAICaller(self.client)

    def extract_topics(self, text: str) -> dict[str, list[str]]:
        prompt_topics = TopicExtractor.generate_prompt(text, [])

        content_topics = self.caller.call(
            prompt=prompt_topics,
            system_message="You are a JSON generator. Output only valid JSON.",
            model=self.MODEL_TOPIC_EXTRACTION,
            temperature=0.0,
            seed=42,
            reasoning_effort="none"
        )

        if content_topics is None:
            return {"Tópicos Gerais": []}

        try:
            data_topics = json.loads(content_topics)
            topics_list = TopicExtractor.parse_topics(data_topics)
        except json.JSONDecodeError:
            return {"Tópicos Gerais": []}

        if not topics_list:
            return {"Tópicos Gerais": []}

        try:
            concepts_map = TopicExtractor.parse_concepts(data_topics)
            if not isinstance(concepts_map, dict):
                concepts_map = {}

            final_map = {}
            for t in topics_list:
                concepts = concepts_map.get(t, [])
                final_map[t] = concepts if isinstance(concepts, list) else []
            return final_map
        except Exception:
            return {t: [] for t in topics_list}
