from modules.materials.ports import TopicAIServicePort

class TopicService:
    def extract_topics(self, text: str, ai_service: TopicAIServicePort) -> dict[str, list[str]]:
        """
        Extracts high-level topics and concepts using AI.
        Returns: { "Topic Name": ["Concept 1", "Concept 2"] }
        """
        # We delegate entirely to AI Service now for better semantics and deduplication
        raw_topics = ai_service.extract_topics(text)
        
        # Blacklist Filtering
        final_topics = {}
        for topic, concepts in raw_topics.items():
            clean_topic = topic
            if topic.lower() in ["outros", "geral", "diversos", "vários"]:
                clean_topic = "Conceitos Gerais"
            
            final_topics[clean_topic] = concepts
            
        return final_topics
