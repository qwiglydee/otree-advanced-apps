from otree.constants import BaseConstants
from otree.decimal import DecimalUnit


class Points(DecimalUnit):
    storage_places = 1
    output_max_places = 1
    output_min_places = 1
    input_places = 1


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = 3

    P1_ROLE = "P1"
    P2_ROLE = "P2"
    P3_ROLE = "P3"
    SEQUENCE = ["P1", "P2", "P3", "P1", "P2", "P3"]

    NUM_TRIALS = 5

    RESPONSES = ['MEOW', 'WOOF']

    SCORING = {
        2: Points(1.0),
        3: Points(10.0),
    }

    ITER_DELAY = 2
