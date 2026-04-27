import random

from otree.models import Session


def get_session_param(session: Session, param: str, /, choices: tuple[str] | list[str], default: str | None = None) -> str:
    value = session.config.get(param, default)
    if value == "random":
        value = random.choice(choices)
    assert value in choices, f"unrecognized value for `{param}` in session settings"
    assert value is not None
    return value
