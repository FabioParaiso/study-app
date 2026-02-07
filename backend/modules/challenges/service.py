from __future__ import annotations

import logging
from datetime import datetime, timezone

import feature_flags
from modules.challenges.calendar import get_local_date, get_week_id, is_training_week, validate_tz_offset
from modules.challenges.calculator import (
    cap_active_seconds,
    is_valid_session,
    min_plausible_active_seconds,
    normalize_score_pct,
    xp_for_first_valid_session,
)
from modules.challenges.constants import CONTINUITY_TARGET_DAYS, CONTINUITY_TARGET_XP, MISSION_BASE_TARGET_DAYS
from modules.challenges.repository import ChallengeRepository
from modules.challenges.tokens import decode_quiz_session_token, parse_issued_at

logger = logging.getLogger(__name__)


class ChallengeService:
    def __init__(self, repo: ChallengeRepository):
        self.repo = repo

    def process_session(
        self,
        *,
        quiz_result_id: int,
        student_id: int,
        quiz_type: str,
        score: int,
        total_questions: int,
        active_seconds: int,
        quiz_session_token: str | None,
    ) -> dict:
        if not feature_flags.is_coop_challenge_enabled():
            return {"applied": False, "reason": "feature_disabled"}

        if not quiz_session_token:
            return {"applied": False, "reason": "token_missing"}

        payload = decode_quiz_session_token(quiz_session_token)
        if payload is None:
            return {"applied": False, "reason": "token_invalid"}

        try:
            token_student_id = int(payload.get("student_id"))
        except (TypeError, ValueError):
            return {"applied": False, "reason": "token_invalid_student"}

        if token_student_id != int(student_id):
            return {"applied": False, "reason": "token_student_mismatch"}

        token_quiz_type = payload.get("quiz_type")
        if isinstance(token_quiz_type, str) and token_quiz_type and token_quiz_type != quiz_type:
            return {"applied": False, "reason": "token_quiz_type_mismatch"}

        jti = payload.get("jti")
        if not isinstance(jti, str) or not jti.strip():
            return {"applied": False, "reason": "token_missing_jti"}

        try:
            issued_at = parse_issued_at(payload)
        except Exception:
            return {"applied": False, "reason": "token_invalid_issued_at"}

        now_utc = datetime.now(timezone.utc)
        server_estimated_seconds = int(max(0.0, (now_utc - issued_at).total_seconds()))
        safe_active_seconds = cap_active_seconds(active_seconds, server_estimated_seconds)

        if safe_active_seconds >= 180 and safe_active_seconds < min_plausible_active_seconds(total_questions):
            logger.warning(
                "Suspiciously fast session for student=%s quiz_result=%s active=%ss questions=%s",
                student_id,
                quiz_result_id,
                safe_active_seconds,
                total_questions,
            )

        result = {"applied": False, "reason": "unknown"}
        try:
            with self.repo.begin_nested():
                if not self.repo.mark_quiz_processed(quiz_result_id):
                    result = {"applied": False, "reason": "duplicate_quiz_result"}
                elif not self.repo.consume_quiz_session_jti(jti.strip(), student_id):
                    result = {"applied": False, "reason": "token_reused"}
                elif not is_valid_session(safe_active_seconds, total_questions):
                    result = {"applied": False, "reason": "session_invalid"}
                else:
                    student = self.repo.get_student(student_id)
                    if student is None:
                        result = {"applied": False, "reason": "student_not_found"}
                    else:
                        quiz_result = self.repo.get_quiz_result(quiz_result_id)
                        if quiz_result is None:
                            result = {"applied": False, "reason": "quiz_result_not_found"}
                        else:
                            tz_offset = validate_tz_offset(student.expected_tz_offset, fallback=0)
                            local_date = get_local_date(quiz_result.created_at, tz_offset)
                            week_id = get_week_id(quiz_result.created_at, tz_offset)
                            training_week = is_training_week(local_date)

                            week, _created_week = self.repo.get_or_create_week(
                                student_id=student.id,
                                week_id=week_id,
                                is_training_week=training_week,
                            )

                            best_score_pct = normalize_score_pct(score, total_questions, quiz_type)
                            day, is_first_valid_session = self.repo.get_or_create_day_activity(
                                challenge_week_id=week.id,
                                local_date=local_date,
                                best_score_pct=best_score_pct,
                                quiz_result_id=quiz_result_id,
                            )

                            xp_awarded = xp_for_first_valid_session(is_first_valid_session)
                            if xp_awarded > 0:
                                self.repo.award_daily_base_xp(student=student, week=week, day=day, xp=xp_awarded)

                            result = {
                                "applied": xp_awarded > 0,
                                "reason": "applied" if xp_awarded > 0 else "already_awarded_today",
                                "xp_awarded": xp_awarded,
                                "week_id": week_id,
                                "local_date": local_date.isoformat(),
                            }

            self.repo.commit()
            return result
        except Exception:
            self.repo.rollback()
            logger.exception("Challenge hook failed for quiz_result_id=%s", quiz_result_id)
            return {"applied": False, "reason": "hook_error"}

    def get_weekly_status(self, student_id: int) -> dict:
        student = self.repo.get_student(student_id)
        if student is None:
            raise ValueError("Student not found")

        now_utc = datetime.now(timezone.utc)
        tz_offset = validate_tz_offset(student.expected_tz_offset, fallback=0)
        local_today = get_local_date(now_utc, tz_offset)
        week_id = get_week_id(now_utc, tz_offset)
        training = is_training_week(local_today)

        student_week = self.repo.get_week(student.id, week_id)
        student_days = self.repo.list_week_days(student_week.id) if student_week else []

        individual = {
            "xp": int(student_week.individual_xp) if student_week else 0,
            "active_days": int(student_week.active_days_count) if student_week else 0,
            "daily_breakdown": [
                {
                    "date": day.local_date.isoformat(),
                    "xp": int(day.daily_xp or 0),
                    "best_score_pct": int(day.best_score_pct or 0),
                    "quality_bonus": bool(day.quality_bonus_applied),
                }
                for day in student_days
            ],
        }

        partner = self.repo.get_student(student.partner_id) if student.partner_id else None
        if partner is None:
            continuity_completed = (
                individual["xp"] >= CONTINUITY_TARGET_XP and individual["active_days"] >= CONTINUITY_TARGET_DAYS
            )
            return {
                "week_id": week_id,
                "is_training_week": training,
                "mode": "solo_continuity",
                "team": None,
                "continuity_mission": {
                    "target_xp": CONTINUITY_TARGET_XP,
                    "target_days": CONTINUITY_TARGET_DAYS,
                    "completed": continuity_completed,
                },
                "individual": individual,
                "partner": None,
                "status": "continuity_completed" if continuity_completed else "continuity_in_progress",
            }

        partner_week = self.repo.get_week(partner.id, week_id)
        partner_xp = int(partner_week.individual_xp) if partner_week else 0
        partner_days_count = int(partner_week.active_days_count) if partner_week else 0
        mission_completed = (
            individual["active_days"] >= MISSION_BASE_TARGET_DAYS
            and partner_days_count >= MISSION_BASE_TARGET_DAYS
        )

        return {
            "week_id": week_id,
            "is_training_week": training,
            "mode": "coop",
            "team": {
                "partner_name": partner.name,
                "team_xp": individual["xp"] + partner_xp,
                "mission_base": {
                    "target_days_each": MISSION_BASE_TARGET_DAYS,
                    "student_days": individual["active_days"],
                    "partner_days": partner_days_count,
                    "completed": mission_completed,
                },
            },
            "individual": individual,
            "partner": {
                "xp": partner_xp,
                "active_days": partner_days_count,
            },
            "status": "completed" if mission_completed else "in_progress",
        }
