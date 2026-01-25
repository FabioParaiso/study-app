from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from modules.analytics.repository import AnalyticsRepository
from modules.analytics.service import AnalyticsService
from modules.materials.repository import MaterialConceptRepository
from services.ports import MaterialConceptPairsRepositoryPort


def get_material_repo(db: Session = Depends(get_db)):
    return MaterialConceptRepository(db)


def get_analytics_repo(db: Session = Depends(get_db)):
    return AnalyticsRepository(db)


def get_analytics_service(
    material_repo: MaterialConceptPairsRepositoryPort = Depends(get_material_repo),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repo)
):
    return AnalyticsService(analytics_repo, material_repo)
