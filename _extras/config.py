import random
from typing import Any

from otree.models import Session


def get_session_param(session: Session, param: str, *, choices: list[str] | None = None) -> Any:
    """Get session config param with validation and random sampling"""

    assert param in session.config, f"missing param `{param}` in session config"
    value = session.config[param]

    if choices is not None:
        if value == "random":
            value = random.choice(choices)
        assert value in choices, f"invalid value for `{param}` in session config"
    else:
        assert value is not None and value != ""
    return value
