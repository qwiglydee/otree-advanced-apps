import random

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models

from _extras.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from units import Points

from .conf import C


def PointsField(**kwargs):
    return models.DecimalField(unit=Points, **kwargs)  # type: ignore internal incompatibility


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()
    total_score = PointsField(initial=0)


class Round(BaseRoundModel):
    player: Player = models.Link(Player)

    total_score = PointsField(initial=0)

    @property
    def condition(self) -> str:
        return self.player.condition

    def init(self):
        pass

    def update(self):
        pass

    progress_trials = models.IntegerField(initial=0)


class Trial(BaseTrialModel):
    iteround: Round = models.Link(Round)

    # TODO: define some fields
    task = models.StringField()

    outcome = models.StringField()
    score = PointsField(initial=None)

    @property
    def condition(self) -> str:
        return self.iteround.condition

    def init(self):
        # TODO: initialize trial
        self.task = "".join(random.choices("aeiou bcdghhxz", k=16))

    def update(self):
        # TODO: calculate intermediate outcomes
        response = Response.last(self)
        if response:
            self.outcome = response.outcome

    def complete(self):
        assert self.outcome is not None
        self.close("COMPLETED")
        self.score = C.SCORING[self.outcome]
        self.iteround.total_score += self.score

    progress_responses = models.IntegerField(initial=0)


class Response(BaseResponseModel):
    trial: Trial = models.Link(Trial)
    player: Player = models.Link(Player)
    response_time = models.IntegerField()

    # TODO: define some fields
    value = models.StringField()
    outcome = models.StringField()

    def evaluate(self):
        # TODO: evaluate response
        assert self.value is not None
        self.outcome = random.choice(C.OUTCOMES)


def set_payoff(player: Player, iteround: Round):
    # use `if` to skip paractice round
    player.total_score += iteround.total_score
    player.payoff = player.total_score.to_real_world_currency(player.session)  # type: ignore


def custom_export(_):
    """This exports all responses joined with their trials/rounds/players"""

    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
        "condition",
        #
        "iteround.pagename",
        "iteround.status",
        "iteround.completion",
        "iteround.processing_time",
        "iteround.total_trials",
        "iteround.total_score",
        #
        "trial.iteration",
        "trial.status",
        "trial.completion",
        "trial.processing_time",
        #
        "trial.task",
        "trial.outcome",
        "trial.score",
        #
        "response.iteration",
        "response.response_time",
        "response.value",
        "response.outcome",
    ]

    for response in Response.totall():
        trial = response.trial
        iteround = trial.iteround
        player = response.player
        # group = player.group

        yield [
            player.session.code,
            player.session.label,
            player.participant.code,
            player.participant.label,
            iteround.condition,
            #
            iteround.pagename,
            iteround.status,
            iteround.completion,
            f"{iteround.processing_time:.01f}" if iteround.processing_time else None,
            iteround.progress_trials,
            iteround.total_score,
            #
            trial.iteration,
            trial.status,
            trial.completion,
            f"{trial.processing_time:.01f}" if trial.processing_time else None,
            #
            trial.task,
            trial.outcome,
            trial.score,
            #
            response.iteration,
            response.response_time,
            response.value,
            response.outcome,
        ]
