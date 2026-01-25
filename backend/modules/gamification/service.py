from modules.gamification.ports import StudentGamificationRepositoryPort


class GamificationServiceError(Exception):
    def __init__(self, message: str, status_code: int = 404):
        super().__init__(message)
        self.status_code = status_code


class GamificationService:
    def __init__(self, repo: StudentGamificationRepositoryPort):
        self.repo = repo

    def add_xp(self, student_id: int, amount: int):
        student = self.repo.update_xp(student_id, amount)
        if not student:
            raise GamificationServiceError("Student not found", status_code=404)
        return student

    def update_avatar(self, student_id: int, avatar: str):
        student = self.repo.update_avatar(student_id, avatar)
        if not student:
            raise GamificationServiceError("Student not found", status_code=404)
        return student

    def update_high_score(self, student_id: int, score: int):
        student = self.repo.update_high_score(student_id, score)
        if not student:
            raise GamificationServiceError("Student not found", status_code=404)
        return student
