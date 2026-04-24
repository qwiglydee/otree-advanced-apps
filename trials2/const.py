from otree.constants import BaseConstants
from _stuff import rand


class C(BaseConstants):
    NAME_IN_URL = __name__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = 2

    P1_ROLE = "P1"
    P2_ROLE = "P2"

    NUM_TRIALS = {
        'Tasks': 3,
    }

    STAGES = ['S1', 'S2', None]
    ROLESMAP = {'S1': 'P1', 'S2': 'P2'}
    STAGEMAP = {'P1': 'S1', 'P2': 'S2'}

    CONDITIONS = ["C0", "C1", "C2"]
    NUMBERS = {
        'C0': rand.Uniform(2, 19),
        'C1': rand.Choices(3, 5, 7, 9, 13, 15, 17, 19),
        'C2': rand.Choices(2, 4, 6, 8, 12, 14, 16, 18),
    }

    SCORING = {
        0: 0,
        1: 1,
        2: 10,
    }

    TRIAL_DELAY = 1
