from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

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
