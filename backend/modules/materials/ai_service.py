import json
from llm_models import get_llm_models
from modules.common.ports import LLMCallerPort
from modules.materials.topic_extractor import TopicExtractor


class TopicAIService:

    def __init__(self, caller: LLMCallerPort | None):
        self.caller = caller
        models = get_llm_models()
        self.model_topic_extraction = models.topic_extraction
        self.reasoning_effort = models.topic_extraction_reasoning or models.reasoning_effort

    def is_available(self) -> bool:
        return bool(self.caller and self.caller.is_available())

    def extract_topics(self, text: str) -> dict[str, list[str]]:
        if not self.is_available():
            return {"Tópicos Gerais": []}
        prompt_topics = TopicExtractor.generate_prompt(text, [])

        content_topics = self.caller.call(
            prompt=prompt_topics,
            system_message="És um gerador de JSON. Devolve apenas JSON válido.",
            model=self.model_topic_extraction,
            temperature=0.0,
            seed=42,
            reasoning_effort=self.reasoning_effort
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
