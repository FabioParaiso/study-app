from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    total_xp = Column(Integer, default=0)
    current_avatar = Column(String, default='mascot')
    high_score = Column(Integer, default=0)
    hashed_password = Column(String, nullable=False) # Password is now mandatory
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    quiz_results = relationship("QuizResult", back_populates="student")
    materials = relationship("StudyMaterial", back_populates="student")
