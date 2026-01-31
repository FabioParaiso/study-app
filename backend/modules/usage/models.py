from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from database import Base


class DailyUsage(Base):
    __tablename__ = "daily_usage"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    day = Column(Date, nullable=False)
    count = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "day", name="uq_daily_usage_student_day"),
    )
