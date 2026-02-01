from datetime import timedelta
from services.token_service import TokenService
from security import create_access_token


def test_create_and_decode_token():
    service = TokenService()
    token = service.create_access_token({"sub": "123"})

    payload = service.decode_access_token(token)

    assert payload is not None
    assert payload.get("sub") == "123"


def test_decode_expired_token_returns_none():
    expired_token = create_access_token({"sub": "123"}, expires_delta=timedelta(seconds=-1))
    service = TokenService()

    payload = service.decode_access_token(expired_token)

    assert payload is None


def test_decode_invalid_token_returns_none():
    service = TokenService()

    payload = service.decode_access_token("not-a-token")

    assert payload is None
