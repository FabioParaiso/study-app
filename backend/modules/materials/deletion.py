from services.ports import MaterialRepositoryPort, QuizRepositoryPort, StudentRepositoryPort


class MaterialDeletionPolicy:
    def __init__(
        self,
        material_repo: MaterialRepositoryPort,
        student_repo: StudentRepositoryPort,
        quiz_repo: QuizRepositoryPort
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
