import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from services.usage_service import UsageService, UsageLimitReached
from dependencies import enforce_ai_quota


def test_usage_service_skips_in_test_mode(monkeypatch):
    monkeypatch.setenv("TEST_MODE", "true")
    repo = Mock()
    service = UsageService(repo)

    remaining = service.check_and_increment(1)

    assert remaining == -1
    repo.increment_if_allowed.assert_not_called()


def test_usage_service_limit_reached(monkeypatch):
    monkeypatch.setenv("TEST_MODE", "false")
    monkeypatch.setenv("DAILY_AI_CALL_LIMIT", "2")
    repo = Mock()
    repo.increment_if_allowed.return_value = (False, 2)
    service = UsageService(repo)

    with pytest.raises(UsageLimitReached):
        service.check_and_increment(1)


def test_usage_service_invalid_limit_defaults(monkeypatch):
    monkeypatch.setenv("TEST_MODE", "false")
    monkeypatch.setenv("DAILY_AI_CALL_LIMIT", "invalid")
    repo = Mock()
    repo.increment_if_allowed.return_value = (True, 1)
    service = UsageService(repo)

    remaining = service.check_and_increment(1)

    assert remaining == 49


def test_usage_service_limit_zero_raises(monkeypatch):
    monkeypatch.setenv("TEST_MODE", "false")
    monkeypatch.setenv("DAILY_AI_CALL_LIMIT", "0")
    repo = Mock()
    service = UsageService(repo)

    with pytest.raises(UsageLimitReached):
        service.check_and_increment(1)


def test_enforce_ai_quota_raises_http_exception(monkeypatch):
    class DummyUser:
        id = 1

    usage_service = Mock()
    usage_service.check_and_increment.side_effect = UsageLimitReached(limit=5)

    with pytest.raises(HTTPException) as exc:
        enforce_ai_quota(current_user=DummyUser(), usage_service=usage_service)

    assert exc.value.status_code == 429
    assert "5" in exc.value.detail
