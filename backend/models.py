from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    total_xp = Column(Integer, default=0)
    current_avatar = Column(String, default='mascot')
    high_score = Column(Integer, default=0)
    hashed_password = Column(String, nullable=False) # Password is now mandatory
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz_results = relationship("QuizResult", back_populates="student")
    materials = relationship("StudyMaterial", back_populates="student")

class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id")) # Link to owner
    source = Column(String, index=True)
    text = Column(Text)
    # topics column removed in favor of relational tables
    
    # New fields for per-material gamification and state
    total_xp = Column(Integer, default=0)
    high_score = Column(Integer, default=0)
    total_questions_answered = Column(Integer, default=0)
    correct_answers_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="materials")
    topics = relationship("Topic", back_populates="material", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    study_material_id = Column(Integer, ForeignKey("study_materials.id"))
    name = Column(String, index=True)
    
    material = relationship("StudyMaterial", back_populates="topics")
    concepts = relationship("Concept", back_populates="topic", cascade="all, delete-orphan")

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    name = Column(String, index=True)

    topic = relationship("Topic", back_populates="concepts")
    analytics = relationship("QuestionAnalytics", back_populates="concept")

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
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True) # Linked to granular concept
    # topic string kept for backward compatibility if needed, but primary link is concept_id
    topic = Column(String, index=True, nullable=True) 
    is_correct = Column(Boolean)
    
    quiz_result = relationship("QuizResult", back_populates="analytics")
    concept = relationship("Concept", back_populates="analytics")
