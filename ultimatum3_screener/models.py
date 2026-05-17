import random
from typing import Self
from collections import Counter

from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.forms import widgets

from _stuff.screening import pre_assign_role

from .conf import C


class Subsession(BaseSubsession):
    @classmethod
    def get_matching(cls, other: BaseSubsession) -> Self:
        return cls.objects_filter(session=other.session).one()

    quelen_p = database.IntegerField(initial=0)
    quelen_r = database.IntegerField(initial=0)

    def track_queues(self, queues: dict[str, list]):
        self.quelen_p = len(queues['P'])
        self.quelen_r = len(queues['R'])
        # print("queues:", self.get_counters())

    def get_counters(self):
        return Counter({
            'P': self.quelen_p,
            'R': self.quelen_r,
        })

    condition = database.StringField()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    @classmethod
    def get_matching(cls, other: BasePlayer) -> Self:
        return cls.objects_filter(participant=other.participant).one()

    age = database.IntegerField()
    gender = database.StringField(
        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
        widget=widgets.RadioSelect
    )
    agreement = database.BooleanField(
        label="I agree",
        widget=widgets.Checkbox
    )
    comprehended = database.BooleanField(
        label="I comprehend",
        choices=[(True, "Yes"), (False, "No")],
        widget=widgets.RadioSelect,
    )

    @property
    def dropout(self):
        return self.participant.status == 'dropout'

    @property
    def misfit(self):
        return self.age < 18 or self.age > 80

    @property
    def unqualified(self):
        return not self.field_maybe_none('comprehended')


def preassign_player(player):
    """Pick a role for new participant
    Using balancing formula to make partners for who is already waiting.
    The waiting queque contains one particular role.

    Probability of selecting pairing role raises with length of the queue.
    https://www.desmos.com/calculator/faylavm1ma

    The formula expected to magically balance both the waiting queue and the screening queue.
    """
    counters = player.subsession.get_counters()
    mostrole, quelen = counters.most_common(1)[0]

    f = 0.5 * pow(1.0 - C.BALANCING, quelen)  # waiting role factor
    roles = [mostrole, C.PARTNEROLES[mostrole]]
    probs = [f, 1.0 - f]
    [picked] = random.choices(roles, probs)

    pre_assign_role(player, picked)
