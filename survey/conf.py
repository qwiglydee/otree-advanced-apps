from otree.api import BaseConstants

from _extras.config import get_session_param


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1
    PLAYERS_PER_GROUP = None

    CONDITIONS = ["C1", "C2"]


def config_condition(session):
    return get_session_param(session, "condition", choices=C.CONDITIONS)
