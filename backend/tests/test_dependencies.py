import pytest
from types import SimpleNamespace
from fastapi import HTTPException
from dependencies import get_current_user


class DummyTokenService:
    def __init__(self, payload):
        self.payload = payload

    def decode_access_token(self, token: str):
        return self.payload


class DummyRepo:
    def __init__(self, student):
        self.student = student

    def get_student(self, student_id: int):
        return self.student


def test_get_current_user_invalid_token():
    token_service = DummyTokenService(payload=None)
    repo = DummyRepo(student=None)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token="bad", repo=repo, token_service=token_service)

    assert exc.value.status_code == 401


def test_get_current_user_missing_sub():
    token_service = DummyTokenService(payload={})
    repo = DummyRepo(student=None)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token="bad", repo=repo, token_service=token_service)

    assert exc.value.status_code == 401


def test_get_current_user_student_not_found():
    token_service = DummyTokenService(payload={"sub": "1"})
    repo = DummyRepo(student=None)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token="bad", repo=repo, token_service=token_service)

    assert exc.value.status_code == 401


def test_get_current_user_success():
    student = SimpleNamespace(id=1)
    token_service = DummyTokenService(payload={"sub": "1"})
    repo = DummyRepo(student=student)

    resolved = get_current_user(token="good", repo=repo, token_service=token_service)

    assert resolved == student
