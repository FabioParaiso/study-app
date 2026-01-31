from datetime import date
import os
from repositories.usage_repository import DailyUsageRepository


class UsageLimitReached(Exception):
    def __init__(self, limit: int):
        self.limit = limit
        super().__init__(f"Daily limit reached: {limit}")


class UsageService:
    def __init__(self, repo: DailyUsageRepository):
        self.repo = repo

    def check_and_increment(self, student_id: int) -> int:
        if os.getenv("TEST_MODE") == "true":
            return -1

        try:
            limit = int(os.getenv("DAILY_AI_CALL_LIMIT", "50"))
        except ValueError:
            limit = 50

        if limit <= 0:
            raise UsageLimitReached(limit)

        allowed, count = self.repo.increment_if_allowed(student_id, date.today(), limit)
        if not allowed:
            raise UsageLimitReached(limit)
        return limit - count
