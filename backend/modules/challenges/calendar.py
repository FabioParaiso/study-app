import os
from datetime import date, datetime, timedelta, timezone

VALID_TZ_RANGE = (-720, 840)  # UTC-12 .. UTC+14


def validate_tz_offset(tz_offset_minutes: int, fallback: int = 0) -> int:
    try:
        value = int(tz_offset_minutes)
    except (TypeError, ValueError):
        return int(fallback)
    if VALID_TZ_RANGE[0] <= value <= VALID_TZ_RANGE[1]:
        return value
    return int(fallback)


def _ensure_utc_datetime(utc_dt: datetime) -> datetime:
    if utc_dt.tzinfo is None:
        return utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(timezone.utc)


def get_local_date(utc_dt: datetime, tz_offset_minutes: int) -> date:
    safe_offset = validate_tz_offset(tz_offset_minutes, fallback=0)
    base = _ensure_utc_datetime(utc_dt)
    local_dt = base + timedelta(minutes=safe_offset)
    return local_dt.date()


def get_week_id(utc_dt: datetime, tz_offset_minutes: int) -> str:
    local_day = get_local_date(utc_dt, tz_offset_minutes)
    iso_year, iso_week, _ = local_day.isocalendar()
    return f"{iso_year}W{iso_week:02d}"


def get_challenge_launch_date() -> date | None:
    raw = os.getenv("CHALLENGE_LAUNCH_DATE")
    if raw is None or not raw.strip():
        return None
    try:
        return date.fromisoformat(raw.strip())
    except ValueError as exc:
        raise ValueError(
            "Invalid CHALLENGE_LAUNCH_DATE. Expected format: YYYY-MM-DD."
        ) from exc


def get_official_start_date(launch_date: date | None) -> date | None:
    if launch_date is None:
        return None
    weekday = launch_date.weekday()  # Monday=0
    if weekday == 0:
        return launch_date
    days_until_monday = 7 - weekday
    return launch_date + timedelta(days=days_until_monday)


def is_training_week(local_date: date, launch_date: date | None = None) -> bool:
    if launch_date is None:
        launch_date = get_challenge_launch_date()
    official_start = get_official_start_date(launch_date)
    if official_start is None:
        return False
    return local_date < official_start
