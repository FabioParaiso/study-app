from modules.challenges.calculator import (
    cap_active_seconds,
    expected_questions_for_type,
    is_valid_session_shape,
    normalize_score_pct,
    xp_for_first_valid_session,
)


def test_expected_questions_for_type():
    assert expected_questions_for_type("multiple-choice") == 10
    assert expected_questions_for_type("short_answer") == 8
    assert expected_questions_for_type("open-ended") == 5
    assert expected_questions_for_type("unknown") is None


def test_is_valid_session_shape_by_quiz_type():
    assert is_valid_session_shape("multiple-choice", 10, 10) == (True, "valid")
    assert is_valid_session_shape("short_answer", 8, 8) == (True, "valid")
    assert is_valid_session_shape("open-ended", 5, 5) == (True, "valid")


def test_is_valid_session_shape_invalid_question_count():
    assert is_valid_session_shape("open-ended", 8, 8) == (False, "invalid_question_count")
    assert is_valid_session_shape("multiple-choice", 9, 9) == (False, "invalid_question_count")


def test_is_valid_session_shape_incomplete_submission():
    assert is_valid_session_shape("short_answer", 8, 7) == (False, "incomplete_submission")


def test_is_valid_session_shape_below_min_questions_and_unknown():
    assert is_valid_session_shape("multiple-choice", 4, 4) == (False, "below_min_questions")
    assert is_valid_session_shape("essay", 10, 10) == (False, "unknown_quiz_type")


def test_xp_for_first_valid_session():
    assert xp_for_first_valid_session(True) == 20
    assert xp_for_first_valid_session(False) == 0


def test_normalize_score_pct_mcq_and_clamp():
    assert normalize_score_pct(4, 5, "multiple-choice") == 80
    assert normalize_score_pct(1, 0, "multiple-choice") == 0
    assert normalize_score_pct(130, 10, "short_answer") == 100
    assert normalize_score_pct(-5, 10, "open-ended") == 0


def test_cap_active_seconds_uses_server_estimate():
    assert cap_active_seconds(300, 100) == 110
    assert cap_active_seconds(90, 100) == 90
    assert cap_active_seconds(-1, 100) == 0
