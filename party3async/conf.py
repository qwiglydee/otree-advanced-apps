from otree.api import BaseConstants

from _extras.config import get_session_param
from units import Points


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = 3

    CONDITIONS = ["C0", "C1", "C2"]

    NUM_TRIALS = 3

    RESPONSES = ["MEOW", "WOOF"]

    # { num_agreed : score }
    SCORING = {
        2: Points(1.0),
        3: Points(10.0),
    }

    ITER_DELAY = 2


def config_condition(session):
    return get_session_param(session, "condition", choices=C.CONDITIONS)
