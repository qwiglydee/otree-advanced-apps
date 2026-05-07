from otree.constants import BaseConstants
from otree.decimal import DecimalUnit

from _stuff import rand


class Points(DecimalUnit):
    storage_places = 2
    output_max_places = 2
    output_min_places = 2
    input_places = 2


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = None

    NUM_TRIALS = {
        'Practice': 3,
        'Main': 10,
    }

    NUM_RETRIES = {
        'Practice': 2,
    }

    CONDITIONS = ["C0", "C1", "C2"]
    NUMBERS = {
        'C0': rand.Uniform(12, 19),
        'C1': rand.Choices(13, 15, 17, 19),
        'C2': rand.Choices(12, 14, 16, 18),
    }

    SCORING = {
        0: Points(0),
        1: Points(10),
    }

    RETRY_DELAY = 1
    TRIAL_DELAY = 2
