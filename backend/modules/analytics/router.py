from fastapi import APIRouter, Depends
from modules.analytics.deps import get_analytics_service
from modules.analytics.service import AnalyticsService
from dependencies import get_current_user
from models import Student

router = APIRouter()

# --- Endpoints ---
@router.get("/analytics/weak-points")
def get_weak_points(
    current_user: Student = Depends(get_current_user),
    material_id: int | None = None,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return analytics_service.get_weak_points(current_user.id, material_id)
