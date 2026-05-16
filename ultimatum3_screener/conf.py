from otree.constants import BaseConstants

from _stuff.config import get_session_param

import ultimatum3 as mainapp


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = None

    ROLES = mainapp.C.ROLES
    PARTNEROLES = mainapp.C.PARTNEROLES
    CONDITIONS = mainapp.C.CONDITIONS
    ENDOWMENT = mainapp.C.ENDOWMENT

    """Balancing factor
    see models.py:preassign_role
     
    0: roles assigned equiprobably
    1: all new participants assigned pairing role
    0 < 0.5 < 1: somewhat exponential
    """
    BALANCING = 0.7


def config_condition(session):
    return get_session_param(session, 'condition', choices=C.CONDITIONS, default=None)
