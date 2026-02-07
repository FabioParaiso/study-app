from __future__ import annotations

from datetime import date
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from modules.auth.models import Student
from modules.challenges.models import (
    ChallengeConsumedQuizSession,
    ChallengeDayActivity,
    ChallengeProcessedQuiz,
    ChallengeWeek,
)
from modules.quizzes.models import QuizResult


class ChallengeRepository:
    def __init__(self, db: Session):
        self.db = db

    def begin_nested(self):
        return self.db.begin_nested()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def _insert_ignore(self, table: str, values: dict, conflict_columns: list[str]) -> bool:
        bind = self.db.get_bind()
        dialect = bind.dialect.name if bind else ""

        columns = list(values.keys())
        columns_sql = ", ".join(columns)
        params_sql = ", ".join(f":{column}" for column in columns)
        where_sql = " AND ".join(f"{column} = :{column}" for column in conflict_columns)
        exists_stmt = text(f"SELECT 1 FROM {table} WHERE {where_sql} LIMIT 1")

        if self.db.execute(exists_stmt, values).first() is not None:
            return False

        if dialect == "sqlite":
            stmt = text(f"INSERT OR IGNORE INTO {table} ({columns_sql}) VALUES ({params_sql})")
            self.db.execute(stmt, values)
            return self.db.execute(exists_stmt, values).first() is not None

        if dialect in {"postgres", "postgresql"}:
            conflict_sql = ", ".join(conflict_columns)
            stmt = text(
                f"INSERT INTO {table} ({columns_sql}) VALUES ({params_sql}) "
                f"ON CONFLICT ({conflict_sql}) DO NOTHING"
            )
            self.db.execute(stmt, values)
            return self.db.execute(exists_stmt, values).first() is not None

        stmt = text(f"INSERT INTO {table} ({columns_sql}) VALUES ({params_sql})")
        self.db.execute(stmt, values)
        return self.db.execute(exists_stmt, values).first() is not None

    def mark_quiz_processed(self, quiz_result_id: int) -> bool:
        return self._insert_ignore(
            table=ChallengeProcessedQuiz.__tablename__,
            values={
                "quiz_result_id": int(quiz_result_id),
                "created_at": datetime.now(timezone.utc),
            },
            conflict_columns=["quiz_result_id"],
        )

    def consume_quiz_session_jti(self, jti: str, student_id: int) -> bool:
        return self._insert_ignore(
            table=ChallengeConsumedQuizSession.__tablename__,
            values={
                "jti": str(jti),
                "student_id": int(student_id),
                "consumed_at": datetime.now(timezone.utc),
            },
            conflict_columns=["jti"],
        )

    def get_student(self, student_id: int) -> Student | None:
        return self.db.query(Student).filter(Student.id == int(student_id)).first()

    def get_quiz_result(self, quiz_result_id: int) -> QuizResult | None:
        return self.db.query(QuizResult).filter(QuizResult.id == int(quiz_result_id)).first()

    def get_week(self, student_id: int, week_id: str) -> ChallengeWeek | None:
        return (
            self.db.query(ChallengeWeek)
            .filter(ChallengeWeek.student_id == int(student_id), ChallengeWeek.week_id == str(week_id))
            .first()
        )

    def get_or_create_week(self, student_id: int, week_id: str, is_training_week: bool) -> tuple[ChallengeWeek, bool]:
        existing = self.get_week(student_id, week_id)
        if existing is not None:
            return existing, False

        week = ChallengeWeek(
            student_id=int(student_id),
            week_id=str(week_id),
            individual_xp=0,
            active_days_count=0,
            is_training_week=bool(is_training_week),
        )
        self.db.add(week)
        self.db.flush()
        return week, True

    def get_or_create_day_activity(
        self,
        *,
        challenge_week_id: int,
        local_date: date,
        best_score_pct: int,
        quiz_result_id: int,
    ) -> tuple[ChallengeDayActivity, bool]:
        existing = (
            self.db.query(ChallengeDayActivity)
            .filter(
                ChallengeDayActivity.challenge_week_id == int(challenge_week_id),
                ChallengeDayActivity.local_date == local_date,
            )
            .first()
        )

        if existing is not None:
            existing.best_score_pct = max(int(existing.best_score_pct or 0), int(best_score_pct or 0))
            existing.last_quiz_result_id = int(quiz_result_id)
            self.db.flush()
            return existing, False

        day = ChallengeDayActivity(
            challenge_week_id=int(challenge_week_id),
            local_date=local_date,
            daily_xp=0,
            best_score_pct=max(0, min(100, int(best_score_pct or 0))),
            quality_bonus_applied=False,
            first_quiz_result_id=int(quiz_result_id),
            last_quiz_result_id=int(quiz_result_id),
        )
        self.db.add(day)
        self.db.flush()
        return day, True

    def award_daily_base_xp(self, *, student: Student, week: ChallengeWeek, day: ChallengeDayActivity, xp: int) -> None:
        safe_xp = max(0, int(xp or 0))
        if safe_xp <= 0:
            return

        day.daily_xp = int(day.daily_xp or 0) + safe_xp
        week.individual_xp = int(week.individual_xp or 0) + safe_xp
        week.active_days_count = int(week.active_days_count or 0) + 1
        student.challenge_xp = int(student.challenge_xp or 0) + safe_xp
        self.db.flush()

    def list_week_days(self, challenge_week_id: int) -> list[ChallengeDayActivity]:
        return (
            self.db.query(ChallengeDayActivity)
            .filter(ChallengeDayActivity.challenge_week_id == int(challenge_week_id))
            .order_by(ChallengeDayActivity.local_date.asc())
            .all()
        )
