from security import create_access_token, decode_access_token
from services.ports import TokenServicePort


class TokenService(TokenServicePort):
    def create_access_token(self, data: dict) -> str:
        return create_access_token(data)

    def decode_access_token(self, token: str) -> dict | None:
        return decode_access_token(token)
