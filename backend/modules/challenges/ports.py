from typing import Any, Protocol


class ChallengeRepositoryPort(Protocol):
    def begin_nested(self) -> Any: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class ChallengeServicePort(Protocol):
    def process_session(
        self,
        *,
        quiz_result_id: int,
        student_id: int,
        quiz_type: str,
        score: int,
        total_questions: int,
        detailed_results_count: int,
        active_seconds: int,
        quiz_session_token: str | None,
    ) -> dict: ...

    def get_weekly_status(self, student_id: int) -> dict: ...
