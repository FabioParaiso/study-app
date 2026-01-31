from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from modules.usage.models import DailyUsage


class DailyUsageRepository:
    def __init__(self, db: Session):
        self.db = db

    def increment_if_allowed(self, student_id: int, day: date, limit: int) -> tuple[bool, int]:
        usage = self.db.execute(
            select(DailyUsage).where(
                DailyUsage.student_id == student_id,
                DailyUsage.day == day,
            )
        ).scalar_one_or_none()

        if usage is None:
            usage = DailyUsage(student_id=student_id, day=day, count=0)
            self.db.add(usage)
            try:
                self.db.flush()
            except IntegrityError:
                self.db.rollback()
                usage = self.db.execute(
                    select(DailyUsage).where(
                        DailyUsage.student_id == student_id,
                        DailyUsage.day == day,
                    )
                ).scalar_one()

        if usage.count >= limit:
            return False, usage.count

        usage.count += 1
        self.db.commit()
        self.db.refresh(usage)
        return True, usage.count
