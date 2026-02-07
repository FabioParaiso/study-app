from modules.challenges.constants import (
    EXPECTED_QUESTIONS_BY_TYPE,
    MAX_ACTIVE_SECONDS_MULTIPLIER,
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


def expected_questions_for_type(quiz_type: str) -> int | None:
    return EXPECTED_QUESTIONS_BY_TYPE.get(str(quiz_type or "").strip())


def is_valid_session_shape(quiz_type: str, total_questions: int, detailed_results_count: int) -> tuple[bool, str]:
    expected_questions = expected_questions_for_type(quiz_type)
    if expected_questions is None:
        return False, "unknown_quiz_type"

    if int(total_questions or 0) < MIN_QUESTIONS:
        return False, "below_min_questions"

    if int(total_questions or 0) != int(expected_questions):
        return False, "invalid_question_count"

    if int(detailed_results_count or 0) != int(total_questions or 0):
        return False, "incomplete_submission"

    return True, "valid"


def xp_for_first_valid_session(is_first_valid_session_of_day: bool) -> int:
    if is_first_valid_session_of_day:
        return XP_BASE_DAILY
    return 0
