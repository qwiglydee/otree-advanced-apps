from otree.api import BaseConstants

from _extras.config import get_session_param
from units import Coins


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1

    CONDITIONS = ["C0", "C1", "C2"]

    NUM_TRIALS = 5

    PLAYERS_PER_GROUP = 2
    P_ROLE = "P"
    R_ROLE = "R"

    STAGES = ["PROPOSING", "RESPONDING"]
    ROLES = {"PROPOSING": "P", "RESPONDING": "R"}

    DECISIONS = ["ACCEPT", "REJECT"]

    ENDOWMENT = {
        "C0": Coins(100),
        "C1": Coins(500),
        "C2": Coins(1000),
    }

    ITER_DELAY = 3


def config_condition(session):
    return get_session_param(session, "condition", choices=C.CONDITIONS)
