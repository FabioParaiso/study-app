from datetime import datetime, timedelta, timezone

from modules.challenges.tokens import create_quiz_session_token, decode_quiz_session_token


def test_quiz_session_token_roundtrip():
    token = create_quiz_session_token(
        student_id=7,
        material_id=13,
        quiz_type="multiple-choice",
    )

    payload = decode_quiz_session_token(token)
    assert payload is not None
    assert payload["student_id"] == 7
    assert payload["material_id"] == 13
    assert payload["quiz_type"] == "multiple-choice"
    assert isinstance(payload.get("jti"), str)


def test_quiz_session_token_expired_returns_none():
    token = create_quiz_session_token(
        student_id=7,
        material_id=13,
        quiz_type="multiple-choice",
        now_utc=datetime.now(timezone.utc) - timedelta(hours=5),
    )
    assert decode_quiz_session_token(token) is None


def test_quiz_session_token_invalid_signature_returns_none():
    token = create_quiz_session_token(student_id=1, material_id=None, quiz_type="short_answer")
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    assert decode_quiz_session_token(tampered) is None
