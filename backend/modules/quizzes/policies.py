import random
import feature_flags
from modules.analytics.ports import AnalyticsServicePort
from modules.quizzes.registry import QuizTypeRegistry


class QuizPolicyError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class QuizUnlockPolicy:
    def __init__(self, material_xp: int, registry: QuizTypeRegistry):
        self.material_xp = material_xp
        self.registry = registry

    def select_strategy(self, quiz_type: str):
        config = self.registry.get_for_generation(quiz_type)
        if not feature_flags.is_coop_challenge_enabled() and self.material_xp < config.min_xp:
            raise QuizPolicyError(
                f"Level Locked. Requires {config.min_xp} XP.",
                status_code=403
            )
        return config.strategy_factory()

    def select_evaluation_strategy(self, quiz_type: str):
        # Evaluation usually doesn't need XP check, but we keep it centralized or separate if needed.
        # For now, we just return the strategy based on type.
        config = self.registry.get_for_evaluation(quiz_type)
        return config.evaluation_factory()


class QuizStrategyFactory:
    def __init__(self, registry: QuizTypeRegistry, policy_cls: type[QuizUnlockPolicy] = QuizUnlockPolicy):
        self.policy_cls = policy_cls
        self.registry = registry

    def select_strategy(self, quiz_type: str, material_xp: int):
        policy = self.policy_cls(material_xp, self.registry)
        return policy.select_strategy(quiz_type)

    def select_evaluation_strategy(self, quiz_type: str):
        # Using 0 XP as evaluation shouldn't trigger unlock checks generally,
        # or we might want to enforce it. For now, we bypass XP check for evaluation selection
        # or we can refactor Policy to separate unlock logic from mapping.
        # Re-using Policy for mapping simplicity effectively.
        policy = self.policy_cls(0, self.registry)
        return policy.select_evaluation_strategy(quiz_type)


class AdaptiveTopicSelector:
    def __init__(self, analytics_service: AnalyticsServicePort):
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
