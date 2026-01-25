from modules.materials import prompts as topic_prompts

class TopicExtractor:
    @staticmethod
    def generate_prompt(text: str, existing_topics: list[str]) -> str:
        return topic_prompts.get_topic_extraction_prompt(text, existing_topics)

    @staticmethod
    def parse_topics(content: dict) -> list[str]:
        topics = content.get("topics", [])
        if not isinstance(topics, list):
            return []

        seen = set()
        cleaned = []
        for topic in topics:
            if not isinstance(topic, str):
                continue
            clean_topic = topic.strip()
            if not clean_topic:
                continue
            key = clean_topic.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(clean_topic)
            if len(cleaned) == 6:
                break

        return cleaned

    @staticmethod
    def parse_concepts(content: dict) -> dict[str, list[str]]:
        return content.get("concepts_map", {})
