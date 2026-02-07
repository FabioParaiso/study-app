from datetime import datetime, timedelta, timezone

from models import Student
from modules.challenges.calendar import get_local_date, get_week_id
from modules.challenges.models import ChallengeDayActivity, ChallengeWeek


def _register(client, name: str) -> tuple[int, dict]:
    response = client.post("/register", json={"name": name, "password": "StrongPass1!"})
    assert response.status_code == 200
    body = response.json()
    user_id = body["user"]["id"]
    token = body["access_token"]
    return user_id, {"Authorization": f"Bearer {token}"}


def test_weekly_status_with_partner(client, db_session):
    student_a_id, headers_a = _register(client, "WeeklyA")
    student_b_id, _headers_b = _register(client, "WeeklyB")

    student_a = db_session.query(Student).filter(Student.id == student_a_id).first()
    student_b = db_session.query(Student).filter(Student.id == student_b_id).first()

    student_a.partner_id = student_b.id
    student_b.partner_id = student_a.id
    student_a.expected_tz_offset = 0
    student_b.expected_tz_offset = 0

    now_utc = datetime.now(timezone.utc)
    week_id = get_week_id(now_utc, 0)
    local_today = get_local_date(now_utc, 0)

    week_a = ChallengeWeek(
        student_id=student_a.id,
        week_id=week_id,
        individual_xp=60,
        active_days_count=3,
        is_training_week=False,
    )
    week_b = ChallengeWeek(
        student_id=student_b.id,
        week_id=week_id,
        individual_xp=40,
        active_days_count=2,
        is_training_week=False,
    )
    db_session.add_all([week_a, week_b])
    db_session.flush()

    day1 = ChallengeDayActivity(
        challenge_week_id=week_a.id,
        local_date=local_today - timedelta(days=2),
        daily_xp=20,
        best_score_pct=70,
        quality_bonus_applied=False,
    )
    day2 = ChallengeDayActivity(
        challenge_week_id=week_a.id,
        local_date=local_today - timedelta(days=1),
        daily_xp=20,
        best_score_pct=80,
        quality_bonus_applied=False,
    )
    day3 = ChallengeDayActivity(
        challenge_week_id=week_a.id,
        local_date=local_today,
        daily_xp=20,
        best_score_pct=90,
        quality_bonus_applied=False,
    )
    db_session.add_all([day1, day2, day3])
    db_session.commit()

    response = client.get("/challenge/weekly-status", headers=headers_a)
    assert response.status_code == 200

    data = response.json()
    assert data["mode"] == "coop"
    assert data["team"]["team_xp"] == 100
    assert data["individual"]["active_days"] == 3
    assert data["partner"]["active_days"] == 2
    assert data["status"] == "in_progress"


def test_weekly_status_solo_continuity_when_no_partner(client, db_session):
    student_id, headers = _register(client, "WeeklySolo")

    student = db_session.query(Student).filter(Student.id == student_id).first()
    student.partner_id = None
    student.expected_tz_offset = 0

    now_utc = datetime.now(timezone.utc)
    week_id = get_week_id(now_utc, 0)

    week = ChallengeWeek(
        student_id=student.id,
        week_id=week_id,
        individual_xp=80,
        active_days_count=3,
        is_training_week=False,
    )
    db_session.add(week)
    db_session.commit()

    response = client.get("/challenge/weekly-status", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["mode"] == "solo_continuity"
    assert data["team"] is None
    assert data["continuity_mission"]["completed"] is True
    assert data["status"] == "continuity_completed"
