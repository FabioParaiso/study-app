from sqlalchemy.orm import Session
from models import QuizResult, StudyMaterial, Student
from modules.materials.ports import MaterialDeletionRepositoryPort, MaterialDeletionTransactionPort
from modules.quizzes.ports import QuizResultCleanupPort
from modules.auth.ports import StudentXpRepositoryPort


class MaterialDeletionPolicy:
    def __init__(
        self,
        material_repo: MaterialDeletionRepositoryPort,
        student_repo: StudentXpRepositoryPort,
        quiz_repo: QuizResultCleanupPort
    ):
        self.material_repo = material_repo
        self.student_repo = student_repo
        self.quiz_repo = quiz_repo

    def delete(self, user_id: int, material_id: int) -> bool:
        stats = self.material_repo.get_stats(user_id, material_id)
        if not stats:
            return False

        total_xp = stats.get("total_xp", 0)
        if total_xp > 0:
            student = self.student_repo.get_student(user_id)
            if student:
                new_total = max(0, student.total_xp - total_xp)
                delta = new_total - student.total_xp
                if delta:
                    self.student_repo.update_xp(user_id, delta)

        self.quiz_repo.delete_results_for_material(material_id)
        return self.material_repo.delete(user_id, material_id)

    def delete_with_cleanup(self, user_id: int, material_id: int) -> bool:
        return self.delete(user_id, material_id)


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

            self.db.query(QuizResult).filter(QuizResult.study_material_id == material_id).delete()
            self.db.delete(material)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error deleting material transactionally: {e}")
            self.db.rollback()
            return False
