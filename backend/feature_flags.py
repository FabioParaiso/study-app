import os


_TRUTHY = {"1", "true", "yes", "on"}


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in _TRUTHY


def is_coop_challenge_enabled() -> bool:
    return env_flag("COOP_CHALLENGE_ENABLED", default=False)


def is_coop_pause_mode_enabled() -> bool:
    return env_flag("COOP_PAUSE_MODE_ENABLED", default=False)
