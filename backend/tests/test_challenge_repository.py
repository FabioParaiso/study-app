from datetime import date, datetime, timezone

from models import QuizResult, Student
from modules.challenges.repository import ChallengeRepository
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
    result = QuizResult(
        student_id=student_id,
        score=7,
        total_questions=10,
        quiz_type="multiple-choice",
        duration_seconds=240,
        active_seconds=210,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(result)
    db_session.commit()
    db_session.refresh(result)
    return result


def test_mark_quiz_processed_is_idempotent(db_session):
    student = _create_student(db_session, "ChallengeRepoUser")
    quiz_result = _create_quiz_result(db_session, student.id)

    repo = ChallengeRepository(db_session)
    assert repo.mark_quiz_processed(quiz_result.id) is True
    assert repo.mark_quiz_processed(quiz_result.id) is False


def test_consume_quiz_session_jti_is_unique(db_session):
    student = _create_student(db_session, "ChallengeRepoUser2")

    repo = ChallengeRepository(db_session)
    assert repo.consume_quiz_session_jti("jti-1", student.id) is True
    assert repo.consume_quiz_session_jti("jti-1", student.id) is False


def test_upsert_week_and_day_and_award_xp(db_session):
    student = _create_student(db_session, "ChallengeRepoUser3")
    quiz_result = _create_quiz_result(db_session, student.id)

    repo = ChallengeRepository(db_session)
    week, created_week = repo.get_or_create_week(student.id, "2026W06", False)
    assert created_week is True

    day, created_day = repo.get_or_create_day_activity(
        challenge_week_id=week.id,
        local_date=date(2026, 2, 7),
        best_score_pct=60,
        quiz_result_id=quiz_result.id,
    )
    assert created_day is True

    repo.award_daily_base_xp(student=student, week=week, day=day, xp=20)
    assert day.daily_xp == 20
    assert week.individual_xp == 20
    assert week.active_days_count == 1
    assert student.challenge_xp == 20

    day2, created_day2 = repo.get_or_create_day_activity(
        challenge_week_id=week.id,
        local_date=date(2026, 2, 7),
        best_score_pct=88,
        quiz_result_id=quiz_result.id,
    )
    assert created_day2 is False
    assert day2.best_score_pct == 88
