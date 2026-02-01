from security import get_password_hash
from modules.quizzes.repository import QuizResultPersistenceRepository
from models import Student, StudyMaterial


def _create_student(db_session, name: str = "QuizUser") -> Student:
    student = Student(name=name, hashed_password=get_password_hash("StrongPass1!"))
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


def _create_material(db_session, student_id: int, source: str = "mat.txt") -> StudyMaterial:
    material = StudyMaterial(
        student_id=student_id,
        source=source,
        text="content",
        is_active=True
    )
    db_session.add(material)
    db_session.commit()
    db_session.refresh(material)
    return material


def test_record_quiz_result_counts_mcq_correct(db_session):
    student = _create_student(db_session, "MCQUser")
    material = _create_material(db_session, student.id, "mcq.txt")

    repo = QuizResultPersistenceRepository(db_session)
    success = repo.record_quiz_result(
        student_id=student.id,
        score=3,
        total=5,
        quiz_type="multiple-choice",
        analytics_data=[],
        material_id=material.id,
        xp_earned=0
    )

    assert success is True
    db_session.refresh(material)
    assert material.correct_answers_count == 3


def test_record_quiz_result_normalizes_open_ended_score(db_session):
    student = _create_student(db_session, "OpenUser")
    material = _create_material(db_session, student.id, "open.txt")

    repo = QuizResultPersistenceRepository(db_session)
    success = repo.record_quiz_result(
        student_id=student.id,
        score=70,
        total=4,
        quiz_type="open-ended",
        analytics_data=[],
        material_id=material.id,
        xp_earned=0
    )

    assert success is True
    db_session.refresh(material)
    assert material.correct_answers_count == 3
