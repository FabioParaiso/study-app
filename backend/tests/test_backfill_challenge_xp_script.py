from datetime import datetime, timezone

import pytest
from sqlalchemy import text

from scripts.backfill_challenge_xp import run_backfill
from security import get_password_hash
from models import QuizResult, Student


def _create_student(db_session, name: str) -> Student:
    student = Student(name=name, hashed_password=get_password_hash("StrongPass1!"))
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


def _add_quiz_result(
    db_session,
    student_id: int,
    *,
    score: int,
    total_questions: int,
    quiz_type: str,
    active_seconds: int,
    created_at: datetime,
):
    item = QuizResult(
        student_id=student_id,
        score=score,
        total_questions=total_questions,
        quiz_type=quiz_type,
        active_seconds=active_seconds,
        duration_seconds=active_seconds,
        created_at=created_at,
    )
    db_session.add(item)
    db_session.commit()


def test_backfill_daily_and_quality_rules(db_session):
    student = _create_student(db_session, "BackfillUser")

    # Day 1: two valid sessions, only one +20, best score reaches quality bonus
    _add_quiz_result(
        db_session,
        student.id,
        score=3,
        total_questions=5,
        quiz_type="multiple-choice",
        active_seconds=200,
        created_at=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
    )
    _add_quiz_result(
        db_session,
        student.id,
        score=5,
        total_questions=5,
        quiz_type="multiple-choice",
        active_seconds=210,
        created_at=datetime(2026, 2, 1, 12, 0, tzinfo=timezone.utc),
    )
    # Invalid session should be ignored
    _add_quiz_result(
        db_session,
        student.id,
        score=100,
        total_questions=10,
        quiz_type="short_answer",
        active_seconds=100,
        created_at=datetime(2026, 2, 1, 15, 0, tzinfo=timezone.utc),
    )
    # Day 2 valid short answer but no quality
    _add_quiz_result(
        db_session,
        student.id,
        score=75,
        total_questions=8,
        quiz_type="short_answer",
        active_seconds=220,
        created_at=datetime(2026, 2, 2, 11, 0, tzinfo=timezone.utc),
    )
    # Day 3 valid open-ended with quality
    _add_quiz_result(
        db_session,
        student.id,
        score=85,
        total_questions=8,
        quiz_type="open-ended",
        active_seconds=240,
        created_at=datetime(2026, 2, 3, 11, 0, tzinfo=timezone.utc),
    )

    result = run_backfill(
        db=db_session,
        student_ids=[student.id],
        student_names=[],
        apply=False,
    )

    assert result["dry_run"] is True
    assert result["summary"]["students_processed"] == 1
    item = result["students"][0]
    assert item["quiz_results_total"] == 5
    assert item["valid_sessions"] == 4
    assert item["active_days"] == 3
    assert item["quality_days"] == 2
    assert item["computed_challenge_xp"] == 70  # 3*20 + 2*5


def test_backfill_ignores_invalid_sessions(db_session):
    student = _create_student(db_session, "InvalidOnly")
    _add_quiz_result(
        db_session,
        student.id,
        score=10,
        total_questions=4,  # invalid total
        quiz_type="multiple-choice",
        active_seconds=500,
        created_at=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
    )
    _add_quiz_result(
        db_session,
        student.id,
        score=90,
        total_questions=10,
        quiz_type="short_answer",
        active_seconds=100,  # invalid active time
        created_at=datetime(2026, 2, 1, 11, 0, tzinfo=timezone.utc),
    )

    result = run_backfill(db=db_session, student_ids=[student.id], student_names=[], apply=False)
    item = result["students"][0]
    assert item["valid_sessions"] == 0
    assert item["active_days"] == 0
    assert item["quality_days"] == 0
    assert item["computed_challenge_xp"] == 0


def test_backfill_apply_fails_without_challenge_xp_column(db_session):
    student = _create_student(db_session, "NoChallengeColumn")
    _add_quiz_result(
        db_session,
        student.id,
        score=5,
        total_questions=5,
        quiz_type="multiple-choice",
        active_seconds=220,
        created_at=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
    )

    with pytest.raises(RuntimeError):
        run_backfill(db=db_session, student_ids=[student.id], student_names=[], apply=True)


def test_backfill_dry_run_does_not_mutate_existing_columns(db_session):
    student = _create_student(db_session, "DryRunOnly")
    original_total_xp = student.total_xp

    _add_quiz_result(
        db_session,
        student.id,
        score=5,
        total_questions=5,
        quiz_type="multiple-choice",
        active_seconds=220,
        created_at=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
    )

    run_backfill(db=db_session, student_ids=[student.id], student_names=[], apply=False)
    refreshed = db_session.query(Student).filter(Student.id == student.id).first()
    assert refreshed is not None
    assert refreshed.total_xp == original_total_xp


def test_backfill_filter_by_name(db_session):
    s1 = _create_student(db_session, "NameFilterA")
    s2 = _create_student(db_session, "NameFilterB")

    _add_quiz_result(
        db_session,
        s1.id,
        score=5,
        total_questions=5,
        quiz_type="multiple-choice",
        active_seconds=220,
        created_at=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
    )
    _add_quiz_result(
        db_session,
        s2.id,
        score=5,
        total_questions=5,
        quiz_type="multiple-choice",
        active_seconds=220,
        created_at=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
    )

    result = run_backfill(db=db_session, student_ids=[], student_names=["NameFilterB"], apply=False)
    assert len(result["students"]) == 1
    assert result["students"][0]["student_name"] == "NameFilterB"

    # Ensure DB not mutated in dry-run
    total = db_session.execute(text("SELECT COUNT(*) FROM students")).scalar_one()
    assert total == 2
