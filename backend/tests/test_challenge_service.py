from datetime import datetime, timedelta, timezone

from models import QuizResult, Student
from modules.challenges.repository import ChallengeRepository
from modules.challenges.service import ChallengeService
from modules.challenges.tokens import create_quiz_session_token
from security import get_password_hash


def _create_student(db_session, name: str, expected_tz_offset: int = 0) -> Student:
    student = Student(
        name=name,
        hashed_password=get_password_hash("StrongPass1!"),
        expected_tz_offset=expected_tz_offset,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


def _create_quiz_result(db_session, student_id: int) -> QuizResult:
    quiz_result = QuizResult(
        student_id=student_id,
        score=7,
        total_questions=10,
        quiz_type="multiple-choice",
        duration_seconds=300,
        active_seconds=250,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(quiz_result)
    db_session.commit()
    db_session.refresh(quiz_result)
    return quiz_result


def test_process_session_feature_flag_off_skips(monkeypatch, db_session):
    monkeypatch.setenv("COOP_CHALLENGE_ENABLED", "false")

    student = _create_student(db_session, "ChallengeSvcOff")
    quiz_result = _create_quiz_result(db_session, student.id)

    service = ChallengeService(ChallengeRepository(db_session))
    result = service.process_session(
        quiz_result_id=quiz_result.id,
        student_id=student.id,
        quiz_type="multiple-choice",
        score=7,
        total_questions=10,
        active_seconds=220,
        quiz_session_token=None,
    )

    assert result["reason"] == "feature_disabled"


def test_process_session_awards_once_and_is_idempotent(monkeypatch, db_session):
    monkeypatch.setenv("COOP_CHALLENGE_ENABLED", "true")

    student = _create_student(db_session, "ChallengeSvcOn")
    quiz_result = _create_quiz_result(db_session, student.id)
    token = create_quiz_session_token(
        student_id=student.id,
        material_id=None,
        quiz_type="multiple-choice",
        now_utc=datetime.now(timezone.utc) - timedelta(minutes=10),
    )

    service = ChallengeService(ChallengeRepository(db_session))

    first = service.process_session(
        quiz_result_id=quiz_result.id,
        student_id=student.id,
        quiz_type="multiple-choice",
        score=8,
        total_questions=10,
        active_seconds=240,
        quiz_session_token=token,
    )
    second = service.process_session(
        quiz_result_id=quiz_result.id,
        student_id=student.id,
        quiz_type="multiple-choice",
        score=8,
        total_questions=10,
        active_seconds=240,
        quiz_session_token=token,
    )

    db_session.refresh(student)

    assert first["applied"] is True
    assert first["xp_awarded"] == 20
    assert second["applied"] is False
    assert second["reason"] in {"duplicate_quiz_result", "token_reused"}
    assert student.challenge_xp == 20


def test_process_session_handles_repository_error(monkeypatch):
    monkeypatch.setenv("COOP_CHALLENGE_ENABLED", "true")

    class _BrokenRepo:
        def begin_nested(self):
            raise RuntimeError("db failure")

        def commit(self):
            return None

        def rollback(self):
            return None

    token = create_quiz_session_token(student_id=1, material_id=None, quiz_type="multiple-choice")
    service = ChallengeService(_BrokenRepo())

    result = service.process_session(
        quiz_result_id=1,
        student_id=1,
        quiz_type="multiple-choice",
        score=8,
        total_questions=10,
        active_seconds=240,
        quiz_session_token=token,
    )

    assert result["reason"] == "hook_error"
