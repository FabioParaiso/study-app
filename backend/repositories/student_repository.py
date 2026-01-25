from sqlalchemy.orm import Session
from models import Student

class StudentRepositoryBase:
    def __init__(self, db: Session):
        self.db = db

    def _get_by_name(self, name: str) -> Student | None:
        return self.db.query(Student).filter(Student.name == name).first()

    def _get_student(self, student_id: int) -> Student | None:
        return self.db.query(Student).filter(Student.id == student_id).first()


class StudentAuthRepository(StudentRepositoryBase):
    def create_student(self, name: str, hashed_password: str) -> Student | None:
        existing_student = self._get_by_name(name)
        if existing_student:
            return None  # User already exists

        # New user
        student = Student(name=name, hashed_password=hashed_password)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def get_by_name(self, name: str) -> Student | None:
        return self._get_by_name(name)


class StudentLookupRepository(StudentRepositoryBase):
    def get_student(self, student_id: int) -> Student | None:
        return self._get_student(student_id)


class StudentXpRepository(StudentRepositoryBase):
    def get_student(self, student_id: int) -> Student | None:
        return self._get_student(student_id)

    def update_xp(self, student_id: int, amount: int):
        student = self._get_student(student_id)
        if student:
            student.total_xp += amount
            self.db.commit()
            self.db.refresh(student)
        return student


class StudentGamificationRepository(StudentRepositoryBase):
    def update_xp(self, student_id: int, amount: int):
        student = self._get_student(student_id)
        if student:
            student.total_xp += amount
            self.db.commit()
            self.db.refresh(student)
        return student

    def update_avatar(self, student_id: int, avatar: str):
        student = self._get_student(student_id)
        if student:
            student.current_avatar = avatar
            self.db.commit()
            self.db.refresh(student)
        return student

    def update_high_score(self, student_id: int, score: int):
        student = self._get_student(student_id)
        if student and score > student.high_score:
            student.high_score = score
            self.db.commit()
            self.db.refresh(student)
        return student
