import random
from modules.analytics.service import AnalyticsService
from modules.quizzes.engine import MultipleChoiceStrategy, OpenEndedStrategy, ShortAnswerStrategy


class QuizPolicyError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class QuizUnlockPolicy:
    def __init__(self, material_xp: int):
        self.material_xp = material_xp

    def select_strategy(self, quiz_type: str):
        if quiz_type == "open-ended":
            if self.material_xp < 900:
                raise QuizPolicyError("Level Locked. Requires 900 XP.", status_code=403)
            return OpenEndedStrategy()
        if quiz_type == "short_answer":
            if self.material_xp < 300:
                raise QuizPolicyError("Level Locked. Requires 300 XP.", status_code=403)
            return ShortAnswerStrategy()
        return MultipleChoiceStrategy()


class AdaptiveTopicSelector:
    def __init__(self, analytics_service: AnalyticsService):
        self.analytics_service = analytics_service

    def select(self, user_id: int, material_id: int | None, requested_topics: list[str] | None):
        priority_topics: list[str] = []
        adaptive_data = self.analytics_service.get_adaptive_topics(user_id, material_id)
        if adaptive_data:
            priority_topics = adaptive_data.get("boost", []) + adaptive_data.get("mastered", [])

        target_topics = requested_topics or []

        if target_topics:
            priority_topics = []
        elif priority_topics:
            target_topics = priority_topics

        return target_topics, priority_topics


class ConceptWhitelistBuilder:
    @staticmethod
    def build(material_topics_data: dict | list, target_topics: list[str] | None) -> list[str]:
        if isinstance(material_topics_data, dict):
            if target_topics:
                concepts_subset: list[str] = []
                concepts_seen: set[str] = set()
                topic_key_map = {k.lower(): k for k in material_topics_data.keys()}

                for user_topic in target_topics:
                    key = topic_key_map.get(user_topic.lower())
                    if not key:
                        continue
                    for concept in material_topics_data.get(key, []):
                        norm = concept.lower()
                        if norm in concepts_seen:
                            continue
                        concepts_seen.add(norm)
                        concepts_subset.append(concept)

                return concepts_subset

            material_concepts: list[str] = []
            for t_concepts in material_topics_data.values():
                material_concepts.extend(t_concepts)
            return material_concepts

        return material_topics_data or []


class QuestionPostProcessor:
    def __init__(self, quiz_type: str | None):
        self.quiz_type = quiz_type

    def apply(self, questions: list[dict]) -> list[dict]:
        if self.quiz_type == "multiple-choice" or not self.quiz_type:
            for question in questions:
                if "options" in question and "correctIndex" in question:
                    correct_answer = question["options"][question["correctIndex"]]
                    random.shuffle(question["options"])
                    question["correctIndex"] = question["options"].index(correct_answer)
        return questions
