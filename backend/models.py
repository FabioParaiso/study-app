from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz_results = relationship("QuizResult", back_populates="student")

class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    text = Column(Text)
    topics = Column(String) # JSON string of topics list
    created_at = Column(DateTime, default=datetime.utcnow)

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id")) # NEW
    study_material_id = Column(Integer, ForeignKey("study_materials.id"), nullable=True) # NEW (Simple link)
    
    score = Column(Integer)
    total_questions = Column(Integer)
    quiz_type = Column(String) # 'multiple' or 'open-ended'
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="quiz_results")
    analytics = relationship("QuestionAnalytics", back_populates="quiz_result")

class QuestionAnalytics(Base):
    __tablename__ = "question_analytics"

    id = Column(Integer, primary_key=True, index=True)
    quiz_result_id = Column(Integer, ForeignKey("quiz_results.id"))
    topic = Column(String, index=True)
    is_correct = Column(Boolean)
    
    quiz_result = relationship("QuizResult", back_populates="analytics")
