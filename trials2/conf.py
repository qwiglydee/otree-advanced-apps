from otree.api import BaseConstants

from _extras import rand
from _extras.config import get_session_param
from units import Points


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = None

    NUM_TRIALS = {"Practice": 3, "Main": 5}

    MAX_RETRIES = {"Practice": 2, "Main": 1}

    CONDITIONS = ["C0", "C1", "C2"]
    NUMBERS = {
        "C0": rand.Uniform(12, 19),
        "C1": rand.Choices(13, 15, 17, 19),
        "C2": rand.Choices(12, 14, 16, 18),
    }

    SCORING = {
        False: Points(0),
        True: Points(10),
    }

    RETRY_DELAY = 1
    ITER_DELAY = 1


def config_condition(session):
    return get_session_param(session, "condition", choices=C.CONDITIONS)
