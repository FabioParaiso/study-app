from feature_flags import env_flag, is_coop_challenge_enabled, is_coop_pause_mode_enabled


def test_env_flag_truthy_values(monkeypatch):
    for raw in ["1", "true", "TRUE", "yes", "on", " On "]:
        monkeypatch.setenv("FLAG_X", raw)
        assert env_flag("FLAG_X", default=False) is True


def test_env_flag_falsy_and_default(monkeypatch):
    monkeypatch.delenv("FLAG_X", raising=False)
    assert env_flag("FLAG_X", default=True) is True
    assert env_flag("FLAG_X", default=False) is False

    for raw in ["0", "false", "no", "off", "", "something"]:
        monkeypatch.setenv("FLAG_X", raw)
        assert env_flag("FLAG_X", default=True) is False


def test_named_coop_flags(monkeypatch):
    monkeypatch.setenv("COOP_CHALLENGE_ENABLED", "true")
    monkeypatch.setenv("COOP_PAUSE_MODE_ENABLED", "1")

    assert is_coop_challenge_enabled() is True
    assert is_coop_pause_mode_enabled() is True
