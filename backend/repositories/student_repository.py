from sqlalchemy.orm import Session
from models import Student

class StudentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_student(self, name: str, hashed_password: str) -> Student | None:
        existing_student = self.db.query(Student).filter(Student.name == name).first()
        if existing_student:
             return None # User already exists

        # New user
        student = Student(name=name, hashed_password=hashed_password)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def get_by_name(self, name: str) -> Student | None:
        return self.db.query(Student).filter(Student.name == name).first()

    def get_student(self, student_id: int) -> Student:
        return self.db.query(Student).filter(Student.id == student_id).first()

    def update_xp(self, student_id: int, amount: int):
        student = self.get_student(student_id)
        if student:
            student.total_xp += amount
            self.db.commit()
            self.db.refresh(student)
        return student

    def update_avatar(self, student_id: int, avatar: str):
        student = self.get_student(student_id)
        if student:
            student.current_avatar = avatar
            self.db.commit()
            self.db.refresh(student)
        return student

    def update_high_score(self, student_id: int, score: int):
        student = self.get_student(student_id)
        if student and score > student.high_score:
            student.high_score = score
            self.db.commit()
            self.db.refresh(student)
        return student
