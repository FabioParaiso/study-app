from sqlalchemy.orm import Session
from models import QuizResult, QuestionAnalytics, StudyMaterial, Student
from modules.materials.ports import MaterialDeletionTransactionPort


class MaterialDeletionTransaction(MaterialDeletionTransactionPort):
    def __init__(self, db: Session):
        self.db = db

    def delete_with_cleanup(self, user_id: int, material_id: int) -> bool:
        try:
            material = (
                self.db.query(StudyMaterial)
                .filter(StudyMaterial.student_id == user_id, StudyMaterial.id == material_id)
                .first()
            )
            if not material:
                return False

            if material.total_xp > 0:
                student = self.db.query(Student).filter(Student.id == user_id).first()
                if student:
                    new_total = max(0, student.total_xp - material.total_xp)
                    student.total_xp = new_total

            quiz_ids = [
                row[0]
                for row in self.db.query(QuizResult.id)
                .filter(QuizResult.study_material_id == material_id)
                .all()
            ]
            if quiz_ids:
                self.db.query(QuestionAnalytics).filter(
                    QuestionAnalytics.quiz_result_id.in_(quiz_ids)
                ).delete(synchronize_session=False)
                self.db.query(QuizResult).filter(
                    QuizResult.id.in_(quiz_ids)
                ).delete(synchronize_session=False)
            self.db.delete(material)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error deleting material transactionally: {e}")
            self.db.rollback()
            return False
