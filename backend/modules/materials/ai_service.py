import json
from modules.common.ports import LLMCallerPort
from modules.materials.topic_extractor import TopicExtractor


class TopicAIService:
    MODEL_TOPIC_EXTRACTION = "gpt-4o-mini"

    def __init__(self, caller: LLMCallerPort | None):
        self.caller = caller

    def is_available(self) -> bool:
        return bool(self.caller and self.caller.is_available())

    def extract_topics(self, text: str) -> dict[str, list[str]]:
        if not self.is_available():
            return {"Tópicos Gerais": []}
        prompt_topics = TopicExtractor.generate_prompt(text, [])

        content_topics = self.caller.call(
            prompt=prompt_topics,
            system_message="És um gerador de JSON. Devolve apenas JSON válido.",
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
