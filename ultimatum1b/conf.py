from otree.api import BaseConstants

from _stuff.config import get_session_param
from units import Coins


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1
    NUM_TRIALS = 5

    PLAYERS_PER_GROUP = None
    ROLES = ["P", "R"]
    PARTNEROLES = {"P": "R", "R": "P"}

    STAGES = ["PROPOSING", "DECIDING"]
    STAGEROLES = {"PROPOSING": "P", "DECIDING": "R"}

    DECISIONS = ["ACCEPT", "REJECT"]

    CONDITIONS = ["C0", "C1", "C2"]

    ENDOWMENT = {
        "C0": Coins(100),
        "C1": Coins(500),
        "C2": Coins(1000),
    }

    ITER_DELAY = 3


def config_condition(session):
    return get_session_param(session, "condition", choices=C.CONDITIONS)


def config_role(session):
    return get_session_param(session, "role", choices=C.ROLES)
