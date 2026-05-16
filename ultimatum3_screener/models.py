import random
from typing import Self

from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.forms import widgets

from _stuff.screening import pre_assign_role

from .conf import C


class Subsession(BaseSubsession):
    @classmethod
    def get_matching(cls, other: BaseSubsession) -> Self:
        return cls.objects_filter(session=other.session).one()

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
        label="I agreee with something something",
        widget=widgets.Checkbox
    )
    comprehended = database.BooleanField(
        label="I've comprehended",
        choices=[(True, "Yes"), (False, "No")],
        widget=widgets.RadioSelect,
    )


def preassign_player(player):
    role = random.choice(C.ROLES)
    pre_assign_role(player, role)
