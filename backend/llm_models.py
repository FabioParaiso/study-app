from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class LLMModelConfig:
    quiz_generation: str
    answer_evaluation: str
    topic_extraction: str
    reasoning_effort: str | None = None
    topic_extraction_reasoning: str | None = None


_ENV_ALIASES = {
    "prod": "production",
    "production": "production",
    "stage": "staging",
    "staging": "staging",
    "dev": "staging",
    "development": "staging",
    "local": "staging",
    "test": "test",
    "testing": "test",
}

_DEFAULT_MODELS = {
    "production": LLMModelConfig(
        quiz_generation="gpt-5.2",
        answer_evaluation="gpt-5.2",
        topic_extraction="gpt-5.2",
        reasoning_effort="low",
        topic_extraction_reasoning="medium",
    ),
    "staging": LLMModelConfig(
        quiz_generation="gpt-4o-mini",
        answer_evaluation="gpt-4o-mini",
        topic_extraction="gpt-4o-mini",
        reasoning_effort="none",
    ),
    "test": LLMModelConfig(
        quiz_generation="gpt-4o-mini",
        answer_evaluation="gpt-4o-mini",
        topic_extraction="gpt-4o-mini",
        reasoning_effort="none",
    ),
}


def _normalize_env(value: str | None) -> str:
    if not value:
        return "staging"
    return value.strip().lower()


def get_app_env() -> str:
    if os.getenv("TEST_MODE") == "true":
        return "test"
    raw = os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or os.getenv("ENV")
    normalized = _normalize_env(raw)
    return _ENV_ALIASES.get(normalized, "staging")


def get_llm_models() -> LLMModelConfig:
    env = get_app_env()
    return _DEFAULT_MODELS.get(env, _DEFAULT_MODELS["staging"])
