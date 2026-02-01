from fastapi import APIRouter, Depends
from modules.analytics.deps import get_analytics_service
from dependencies import get_current_user
from models import Student
from modules.analytics.ports import AnalyticsServicePort

router = APIRouter()

# --- Endpoints ---
@router.get("/analytics/weak-points")
def get_weak_points(
    current_user: Student = Depends(get_current_user),
    material_id: int | None = None,
    analytics_service: AnalyticsServicePort = Depends(get_analytics_service)
):
    return analytics_service.get_weak_points(current_user.id, material_id)


@router.get("/analytics/metrics")
def get_recent_metrics(
    current_user: Student = Depends(get_current_user),
    days: int = 30,
    tz_offset_minutes: int = 0,
    analytics_service: AnalyticsServicePort = Depends(get_analytics_service)
):
    return analytics_service.get_recent_metrics(
        current_user.id,
        days=days,
        tz_offset_minutes=tz_offset_minutes
    )
