from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id")) # NEW
    study_material_id = Column(Integer, ForeignKey("study_materials.id"), nullable=True) # NEW (Simple link)
    
    score = Column(Integer)
    total_questions = Column(Integer)
    quiz_type = Column(String) # 'multiple-choice', 'short_answer', or 'open-ended'
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="quiz_results")
    analytics = relationship("QuestionAnalytics", back_populates="quiz_result", cascade="all, delete-orphan")

class QuestionAnalytics(Base):
    __tablename__ = "question_analytics"

    id = Column(Integer, primary_key=True, index=True)
    quiz_result_id = Column(Integer, ForeignKey("quiz_results.id"))
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True) # Linked to granular concept
    # topic string kept for backward compatibility if needed, but primary link is concept_id
    topic = Column(String, index=True, nullable=True) 
    is_correct = Column(Boolean)
    
    quiz_result = relationship("QuizResult", back_populates="analytics")
    concept = relationship("Concept", back_populates="analytics")
