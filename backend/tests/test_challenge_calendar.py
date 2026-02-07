from datetime import date, datetime, timezone

import pytest

from modules.challenges.calendar import (
    get_challenge_launch_date,
    get_local_date,
    get_official_start_date,
    get_week_id,
    is_training_week,
    validate_tz_offset,
)


def test_validate_tz_offset_range_and_fallback():
    assert validate_tz_offset(0) == 0
    assert validate_tz_offset(840) == 840
    assert validate_tz_offset(-720) == -720
    assert validate_tz_offset(999, fallback=60) == 60
    assert validate_tz_offset("x", fallback=-30) == -30


def test_get_local_date_and_week_id_around_boundary():
    dt = datetime(2026, 2, 8, 23, 59, tzinfo=timezone.utc)  # Sunday UTC

    assert get_local_date(dt, 0) == date(2026, 2, 8)
    assert get_week_id(dt, 0) == "2026W06"

    # +60 moves to Monday local week
    assert get_local_date(dt, 60) == date(2026, 2, 9)
    assert get_week_id(dt, 60) == "2026W07"

    # -60 stays in Sunday week
    assert get_local_date(dt, -60) == date(2026, 2, 8)
    assert get_week_id(dt, -60) == "2026W06"


def test_training_week_rules_with_monday_launch(monkeypatch):
    monkeypatch.setenv("CHALLENGE_LAUNCH_DATE", "2026-02-09")  # Monday
    launch_date = get_challenge_launch_date()
    assert launch_date == date(2026, 2, 9)
    assert get_official_start_date(launch_date) == date(2026, 2, 9)

    assert is_training_week(date(2026, 2, 8), launch_date=launch_date) is True
    assert is_training_week(date(2026, 2, 9), launch_date=launch_date) is False


def test_training_week_rules_with_midweek_launch(monkeypatch):
    monkeypatch.setenv("CHALLENGE_LAUNCH_DATE", "2026-02-11")  # Wednesday
    launch_date = get_challenge_launch_date()
    assert launch_date == date(2026, 2, 11)
    assert get_official_start_date(launch_date) == date(2026, 2, 16)  # next Monday

    assert is_training_week(date(2026, 2, 15), launch_date=launch_date) is True
    assert is_training_week(date(2026, 2, 16), launch_date=launch_date) is False


def test_challenge_launch_date_invalid(monkeypatch):
    monkeypatch.setenv("CHALLENGE_LAUNCH_DATE", "11-02-2026")
    with pytest.raises(ValueError):
        get_challenge_launch_date()
