from modules.challenges.constants import (
    MAX_ACTIVE_SECONDS_MULTIPLIER,
    MIN_ACTIVE_SECONDS,
    MIN_QUESTIONS,
    MIN_SECONDS_PER_QUESTION_HEURISTIC,
    XP_BASE_DAILY,
)


def normalize_score_pct(score: int, total_questions: int, quiz_type: str) -> int:
    if quiz_type == "multiple-choice":
        if int(total_questions or 0) <= 0:
            return 0
        raw_pct = (float(score or 0) / float(total_questions)) * 100.0
    else:
        raw_pct = float(score or 0)
    return int(max(0.0, min(100.0, raw_pct)))


def cap_active_seconds(active_seconds: int, server_estimated_seconds: int) -> int:
    reported = max(0, int(active_seconds or 0))
    estimate = max(0, int(server_estimated_seconds or 0))
    max_plausible = int(estimate * MAX_ACTIVE_SECONDS_MULTIPLIER)
    return min(reported, max_plausible)


def min_plausible_active_seconds(total_questions: int) -> int:
    questions = max(0, int(total_questions or 0))
    return questions * MIN_SECONDS_PER_QUESTION_HEURISTIC


def is_valid_session(active_seconds: int, total_questions: int) -> bool:
    return int(active_seconds or 0) >= MIN_ACTIVE_SECONDS and int(total_questions or 0) >= MIN_QUESTIONS


def xp_for_first_valid_session(is_first_valid_session_of_day: bool) -> int:
    if is_first_valid_session_of_day:
        return XP_BASE_DAILY
    return 0
