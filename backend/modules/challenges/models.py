from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class ChallengeWeek(Base):
    __tablename__ = "challenge_week"
    __table_args__ = (UniqueConstraint("student_id", "week_id", name="uq_challenge_week_student_week"),)

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    week_id = Column(String(10), nullable=False, index=True)
    individual_xp = Column(Integer, nullable=False, default=0)
    active_days_count = Column(Integer, nullable=False, default=0)
    is_training_week = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    day_activities = relationship(
        "ChallengeDayActivity",
        back_populates="challenge_week",
        cascade="all, delete-orphan",
    )


class ChallengeDayActivity(Base):
    __tablename__ = "challenge_day_activity"
    __table_args__ = (UniqueConstraint("challenge_week_id", "local_date", name="uq_challenge_day_week_date"),)

    id = Column(Integer, primary_key=True, index=True)
    challenge_week_id = Column(Integer, ForeignKey("challenge_week.id", ondelete="CASCADE"), nullable=False, index=True)
    local_date = Column(Date, nullable=False, index=True)
    daily_xp = Column(Integer, nullable=False, default=0)
    best_score_pct = Column(Integer, nullable=False, default=0)
    quality_bonus_applied = Column(Boolean, nullable=False, default=False)
    first_quiz_result_id = Column(Integer, ForeignKey("quiz_results.id"), nullable=True)
    last_quiz_result_id = Column(Integer, ForeignKey("quiz_results.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    challenge_week = relationship("ChallengeWeek", back_populates="day_activities")


class ChallengeProcessedQuiz(Base):
    __tablename__ = "challenge_processed_quiz"

    id = Column(Integer, primary_key=True, index=True)
    quiz_result_id = Column(Integer, ForeignKey("quiz_results.id"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ChallengeConsumedQuizSession(Base):
    __tablename__ = "challenge_consumed_quiz_session"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(128), nullable=False, unique=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    consumed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
