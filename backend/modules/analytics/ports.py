from typing import Protocol, TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    pass


class AnalyticsServicePort(Protocol):
    def get_weak_points(self, student_id: int, material_id: int | None = None) -> Any: ...
    def get_adaptive_topics(self, student_id: int, material_id: int | None = None) -> Any: ...


class AnalyticsRepositoryPort(Protocol):
    def fetch_question_analytics(self, student_id: int, material_id: int | None = None) -> List[Dict]: ...
