from otree.api import BaseConstants

from _extras.config import get_session_param
from units import Points


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = None

    CONDITIONS = ["C0", "C1", "C2"]

    NUM_TRIALS = {
        "Round1": 3,
        "Round2": 5,
    }

    DECISIONS = ["FOO", "BAR"]
    OUTCOMES = ["A", "B", "C"]

    # map outcome to points
    SCORING = {
        "A": Points(0),
        "B": Points(5),
        "C": Points(10),
    }

    ITER_DELAY = 2


def config_condition(session):
    return get_session_param(session, "condition", choices=C.CONDITIONS)
