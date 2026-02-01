from llm_models import get_app_env, get_llm_models


def _clear_env(monkeypatch):
    for key in (
        "APP_ENV",
        "ENVIRONMENT",
        "ENV",
        "TEST_MODE",
        "LLM_MODEL_QUIZ_GENERATION",
        "LLM_MODEL_ANSWER_EVALUATION",
        "LLM_MODEL_TOPIC_EXTRACTION",
        "LLM_REASONING_EFFORT",
    ):
        monkeypatch.delenv(key, raising=False)


def test_get_app_env_defaults_to_staging(monkeypatch):
    _clear_env(monkeypatch)
    assert get_app_env() == "staging"


def test_get_app_env_dev_aliases_to_staging(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("APP_ENV", "development")
    assert get_app_env() == "staging"


def test_get_app_env_test_mode_overrides(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("TEST_MODE", "true")
    assert get_app_env() == "test"


def test_llm_models_production_defaults(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    models = get_llm_models()
    assert models.quiz_generation == "gpt-5.2"
    assert models.answer_evaluation == "gpt-5.2"
    assert models.topic_extraction == "gpt-5.2"
    assert models.reasoning_effort == "low"


def test_llm_models_staging_defaults(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("APP_ENV", "staging")
    models = get_llm_models()
    assert models.quiz_generation == "gpt-4o-mini"
    assert models.answer_evaluation == "gpt-4o-mini"
    assert models.topic_extraction == "gpt-4o-mini"
    assert models.reasoning_effort == "none"


def test_llm_models_ignore_env_overrides(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LLM_MODEL_QUIZ_GENERATION", "gpt-4o-mini")
    monkeypatch.setenv("LLM_MODEL_ANSWER_EVALUATION", "gpt-4o-mini")
    monkeypatch.setenv("LLM_MODEL_TOPIC_EXTRACTION", "gpt-4o-mini")
    monkeypatch.setenv("LLM_REASONING_EFFORT", "high")
    models = get_llm_models()
    assert models.quiz_generation == "gpt-5.2"
    assert models.answer_evaluation == "gpt-5.2"
    assert models.topic_extraction == "gpt-5.2"
    assert models.reasoning_effort == "low"
