import random
from collections import Counter
from typing import Self

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models, widgets

from _extras.screening import pre_assign_role
from units import Coins

from .conf import C, partnerole


def PointsField(**kwargs):
    return models.DecimalField(unit=Coins, **kwargs)  # type: ignore internal incompatibility


class Subsession(BaseSubsession):
    @classmethod
    def get_matching(cls, other: BaseSubsession) -> Self:
        return cls.objects_filter(session=other.session).one()  # type: ignore

    quelen_p = models.IntegerField(initial=0)
    quelen_r = models.IntegerField(initial=0)

    def track_queues(self, queues: dict[str, list]):
        self.quelen_p = len(queues["P"])
        self.quelen_r = len(queues["R"])
        # print("queues:", self.get_counters())

    def get_counters(self):
        return Counter({
            "P": self.quelen_p,
            "R": self.quelen_r,
        })

    condition = models.StringField()

    def preassign_player(self, player: BasePlayer):
        """Pick a role for new participant
        The newcomer role is selectied to compensate waiting queue.

        The algorithm is expected to magically balance
        both waiting queue (in the main app) and newcomers queue (in the screener app).

        https://www.desmos.com/calculator/faylavm1ma
        """
        waiting, quelen = self.get_counters().most_common(1)[0]
        f = 0.5 * pow(1.0 - C.BALANCING, quelen)  # the balancing factor
        picked = random.choices([waiting, partnerole(waiting)], [f, 1.0 - f], k=1)[0]
        pre_assign_role(player, picked)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    @classmethod
    def get_matching(cls, other: BasePlayer) -> Self:
        return cls.objects_filter(participant=other.participant).one()  # type: ignore

    age = models.IntegerField()
    gender = models.StringField(choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], widget=widgets.RadioSelect)
    agreement = models.BooleanField(label="I agree", widget=widgets.Checkbox)
    comprehended = models.BooleanField(
        label="I comprehend",
        choices=[(True, "Yes"), (False, "No")],
        widget=widgets.RadioSelect,
    )

    @property
    def dropout(self):
        return self.participant.status == "dropout"

    @property
    def misfit(self):
        return self.age < 18 or self.age > 80

    @property
    def unqualified(self):
        return self.field_maybe_none("comprehended") is False

    @property
    def condition(self) -> str:
        return self.subsession.condition  # type: ignore
