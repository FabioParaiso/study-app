from modules.challenges.calculator import (
    cap_active_seconds,
    is_valid_session,
    normalize_score_pct,
    xp_for_first_valid_session,
)


def test_is_valid_session_thresholds():
    assert is_valid_session(180, 5) is True
    assert is_valid_session(179, 5) is False
    assert is_valid_session(180, 4) is False


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
