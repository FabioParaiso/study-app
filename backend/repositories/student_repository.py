from sqlalchemy.orm import Session
from models import Student

class StudentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_student(self, name: str) -> Student:
        student = self.db.query(Student).filter(Student.name == name).first()
        if not student:
            student = Student(name=name)
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)
        return student

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
