from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

from modules.challenges.constants import QUIZ_SESSION_TOKEN_EXP_HOURS
from security import ALGORITHM, SECRET_KEY


class QuizSessionTokenError(Exception):
    pass


def create_quiz_session_token(
    *,
    student_id: int,
    material_id: int | None,
    quiz_type: str,
    now_utc: datetime | None = None,
) -> str:
    issued_at = now_utc or datetime.now(timezone.utc)
    if issued_at.tzinfo is None:
        issued_at = issued_at.replace(tzinfo=timezone.utc)

    payload = {
        "student_id": int(student_id),
        "material_id": int(material_id) if material_id is not None else None,
        "quiz_type": str(quiz_type),
        "issued_at": int(issued_at.timestamp()),
        "jti": uuid4().hex,
        "exp": issued_at + timedelta(hours=QUIZ_SESSION_TOKEN_EXP_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_quiz_session_token(token: str) -> dict | None:
    if not token or not token.strip():
        return None

    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def parse_issued_at(payload: dict) -> datetime:
    raw = payload.get("issued_at")
    try:
        ts = int(raw)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (TypeError, ValueError, OSError) as exc:
        raise QuizSessionTokenError("Invalid issued_at in quiz_session_token") from exc
