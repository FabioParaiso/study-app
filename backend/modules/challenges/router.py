from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_challenge_service, get_current_user
from modules.auth.models import Student
from modules.challenges.ports import ChallengeServicePort

router = APIRouter(prefix="/challenge", tags=["challenge"])


@router.get("/weekly-status")
def get_weekly_status(
    current_user: Student = Depends(get_current_user),
    challenge_service: ChallengeServicePort = Depends(get_challenge_service),
):
    try:
        return challenge_service.get_weekly_status(current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
