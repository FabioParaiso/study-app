import pytest
from sqlalchemy import text

from scripts.pair_students import StudentSelector, run_pairing
from security import get_password_hash
from models import Student


def _create_student(db_session, name: str) -> Student:
    student = Student(name=name, hashed_password=get_password_hash("StrongPass1!"))
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


def _add_partner_column(db_session):
    db_session.execute(text("ALTER TABLE students ADD COLUMN partner_id INTEGER"))
    db_session.commit()


def _partner_of(db_session, student_id: int):
    return db_session.execute(
        text("SELECT partner_id FROM students WHERE id = :id"),
        {"id": student_id},
    ).scalar_one()


def test_pairing_fails_without_partner_column(db_session):
    a = _create_student(db_session, "A_NoCol")
    b = _create_student(db_session, "B_NoCol")

    with pytest.raises(RuntimeError):
        run_pairing(
            db=db_session,
            a_selector=StudentSelector(student_id=a.id),
            b_selector=StudentSelector(student_id=b.id),
            apply=False,
        )


def test_pairing_by_id_and_name_with_cleanup_and_symmetry(db_session):
    _add_partner_column(db_session)

    a = _create_student(db_session, "Alice")
    b = _create_student(db_session, "Bianca")
    c = _create_student(db_session, "Carla")
    d = _create_student(db_session, "Diana")

    # Existing pairs: A<->C and B<->D
    db_session.execute(
        text("UPDATE students SET partner_id = :partner WHERE id = :id"),
        [{"id": a.id, "partner": c.id}, {"id": c.id, "partner": a.id}, {"id": b.id, "partner": d.id}, {"id": d.id, "partner": b.id}],
    )
    db_session.commit()

    result = run_pairing(
        db=db_session,
        a_selector=StudentSelector(student_id=a.id),
        b_selector=StudentSelector(student_name="Bianca"),
        apply=True,
    )

    assert result["dry_run"] is False
    assert _partner_of(db_session, a.id) == b.id
    assert _partner_of(db_session, b.id) == a.id
    assert _partner_of(db_session, c.id) is None
    assert _partner_of(db_session, d.id) is None
    assert set(result["ids_cleared_before_pairing"]) >= {a.id, b.id, c.id, d.id}


def test_pairing_dry_run_does_not_change_data(db_session):
    _add_partner_column(db_session)

    a = _create_student(db_session, "DryA")
    b = _create_student(db_session, "DryB")

    result = run_pairing(
        db=db_session,
        a_selector=StudentSelector(student_name="DryA"),
        b_selector=StudentSelector(student_name="DryB"),
        apply=False,
    )

    assert result["dry_run"] is True
    assert _partner_of(db_session, a.id) is None
    assert _partner_of(db_session, b.id) is None


def test_pairing_rejects_same_student(db_session):
    _add_partner_column(db_session)
    a = _create_student(db_session, "SelfPair")

    with pytest.raises(ValueError):
        run_pairing(
            db=db_session,
            a_selector=StudentSelector(student_id=a.id),
            b_selector=StudentSelector(student_name="SelfPair"),
            apply=True,
        )
