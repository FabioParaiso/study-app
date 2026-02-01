import pytest
from security import get_password_hash
from modules.materials.repository import MaterialReadRepository
from modules.materials.deletion import MaterialDeletionTransaction
from models import Student, StudyMaterial, QuizResult, QuestionAnalytics


def _create_student(db_session, name: str = "User1") -> Student:
    student = Student(name=name, hashed_password=get_password_hash("StrongPass1!"))
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


def test_activate_material_not_found_keeps_active(db_session):
    student = _create_student(db_session, "ActiveUser")

    active_material = StudyMaterial(
        student_id=student.id,
        source="active.txt",
        text="active",
        is_active=True
    )
    inactive_material = StudyMaterial(
        student_id=student.id,
        source="inactive.txt",
        text="inactive",
        is_active=False
    )
    db_session.add_all([active_material, inactive_material])
    db_session.commit()

    repo = MaterialReadRepository(db_session)
    success = repo.activate(student.id, 9999)

    assert success is False
    db_session.refresh(active_material)
    db_session.refresh(inactive_material)
    assert active_material.is_active is True
    assert inactive_material.is_active is False


def test_activate_material_switches_active(db_session):
    student = _create_student(db_session, "SwitchUser")

    active_material = StudyMaterial(
        student_id=student.id,
        source="active.txt",
        text="active",
        is_active=True
    )
    target_material = StudyMaterial(
        student_id=student.id,
        source="target.txt",
        text="target",
        is_active=False
    )
    db_session.add_all([active_material, target_material])
    db_session.commit()

    repo = MaterialReadRepository(db_session)
    success = repo.activate(student.id, target_material.id)

    assert success is True
    db_session.refresh(active_material)
    db_session.refresh(target_material)
    assert active_material.is_active is False
    assert target_material.is_active is True


def test_delete_material_with_cleanup_updates_xp_and_analytics(db_session):
    student = _create_student(db_session, "DeleteUser")
    student.total_xp = 100

    material = StudyMaterial(
        student_id=student.id,
        source="delete.txt",
        text="delete",
        is_active=True,
        total_xp=40
    )
    db_session.add(material)
    db_session.commit()

    quiz_result = QuizResult(
        student_id=student.id,
        study_material_id=material.id,
        score=3,
        total_questions=5,
        quiz_type="multiple-choice"
    )
    db_session.add(quiz_result)
    db_session.flush()

    analytics = QuestionAnalytics(
        quiz_result_id=quiz_result.id,
        topic="Topic",
        is_correct=True
    )
    db_session.add(analytics)
    db_session.commit()

    deletion = MaterialDeletionTransaction(db_session)
    success = deletion.delete_with_cleanup(student.id, material.id)

    assert success is True
    assert db_session.query(StudyMaterial).count() == 0
    assert db_session.query(QuizResult).count() == 0
    assert db_session.query(QuestionAnalytics).count() == 0

    db_session.refresh(student)
    assert student.total_xp == 60
