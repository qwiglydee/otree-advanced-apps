from otree.constants import BaseConstants
from otree.decimal import DecimalUnit


class Points(DecimalUnit):
    storage_places = 2
    output_max_places = 2
    output_min_places = 2
    input_places = 2


class C(BaseConstants):
    NAME_IN_URL = __name__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = None

    NUM_TRIALS = {
        'Tasks': 3,
    }

    CONDITIONS = ["C0", "C1", "C2"]

    SCORING = {
        0: Points(0),
        1: Points(10),
    }

    TRIAL_DELAY = 1
    RETRY_DELAY = 0.5
