from pydantic import BaseModel


class ChallengeDayBreakdown(BaseModel):
    date: str
    xp: int
    best_score_pct: int
    quality_bonus: bool


class WeeklyStatusResponse(BaseModel):
    week_id: str
    is_training_week: bool
    mode: str
    team: dict | None
    individual: dict
    partner: dict | None
    status: str
