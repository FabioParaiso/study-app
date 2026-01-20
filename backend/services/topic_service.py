from services.ai_service import AIService

class TopicService:
    @staticmethod
    def extract_topics(text: str, ai_service: AIService, existing_topics: list[str]) -> list[str]:
        """
        Extracts high-level topics using AI, ensuring reuse of existing topics to avoid duplication.
        """
        # We delegate entirely to AI Service now for better semantics and deduplication
        return ai_service.extract_topics(text, existing_topics)
