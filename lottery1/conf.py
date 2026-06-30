import random

from otree.api import BaseConstants

from _extras import rand
from _extras.config import get_session_param


class C(BaseConstants):
    NAME_IN_URL = __package__
    NUM_ROUNDS = 1  # should be =1
    PLAYERS_PER_GROUP = None

    CONDITIONS = ["C0", "C1", "C2"]
    DISCLOSURES = ["FULL", "CHOICE"]

    NUM_TRIALS = {
        "Practice": 3,
        "Main": 5,
    }

    CHOICES = ["A", "B", "C"]
    LABELS = {1: "foo", 2: "bar", 3: "baz"}  # by screen position

    PARAMS = {
        "C0": {
            "x": rand.Const(+1.0),
            "y": rand.Const(-1.0),
            "z": 10.0,
            "std": 1.0,
        },
        "C1": {
            "x": rand.Normal(+1.0, 1.0),
            "y": rand.Normal(-1.0, 1.0),
            "z": 10.0,
            "std": 1.0,
        },
        "C2": {
            "x": rand.Uniform(0.0, +2.0),
            "y": rand.Uniform(-2.0, 0.0),
            "z": 10.0,
            "std": 1.0,
        },
    }

    ITER_DELAY = 1


def config_condition(session):
    return get_session_param(session, "condition", choices=C.CONDITIONS)


def config_disclosure(session):
    return get_session_param(session, "disclosure", choices=C.DISCLOSURES)


def config_layout():
    layout = random.sample(C.CHOICES, k=len(C.CHOICES))
    return "".join(layout)
