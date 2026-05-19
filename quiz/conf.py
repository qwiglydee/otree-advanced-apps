from otree.api import BaseConstants

from _stuff.config import get_session_param
from units import Points


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = None

    NUM_TRIALS = {
        "Practice": 3,
        "Main": 5,
    }

    CONDITIONS = ["C0", "C1", "C2"]

    SCORING = {
        0: Points(0),
        1: Points(10),
    }

    RETRY_DELAY = 1
    ITER_DELAY = 1


def config_condition(session):
    return get_session_param(session, "condition", C.CONDITIONS)
