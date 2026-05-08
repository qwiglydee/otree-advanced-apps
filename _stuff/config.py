import random

from otree.models import Session


def get_session_param(session: Session, param: str, /, choices: tuple[str] | list[str], default: str | None = "random") -> str:
    """Get session config param
    - check validity agains possible `choices`
    - sets default value if missing
    - randomly samples value from choices when set to `random`
    """
    value = session.config.get(param, default)
    if value == "random":
        return random.choice(choices)
    assert value in choices, f"invalid value for `{param}` in session settings"
    return value
