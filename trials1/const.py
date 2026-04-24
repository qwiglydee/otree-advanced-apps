from otree.constants import BaseConstants
from _stuff import rand


class C(BaseConstants):
    NAME_IN_URL = __name__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = None

    NUM_TRIALS = {
        'Tasks': 3,
    }

    NUM_RETRIES = {
        'Tasks': 3,
    }

    CONDITIONS = ["C0", "C1", "C2"]
    NUMBERS = {
        'C0': rand.Uniform(2, 19),
        'C1': rand.Choices(3, 5, 7, 9, 13, 15, 17, 19),
        'C2': rand.Choices(2, 4, 6, 8, 12, 14, 16, 18),
    }

    SCORING = {
        0: 0,
        1: 10,
    }

    TRIAL_DELAY = 1
    RETRY_DELAY = 0.5
