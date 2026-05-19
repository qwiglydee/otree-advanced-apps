from collections import Counter

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models

from _stuff.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from units import Points

from .conf import C


def PointsField():
    return models.DecimalField(unit=Points, initial=0)  # type: ignore internal incompatibility


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    total_score = PointsField()
    progress_round = models.IntegerField()
    progress_trial = models.IntegerField()


class Round(BaseRoundModel):
    group: Group = models.Link(Group)
    total_score = PointsField()

    def init(self):
        pass

    def update(self):
        pass

    progress_trials = models.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = models.Link(Round)

    success = models.IntegerField()
    score = PointsField()

    def init(self):
        pass

    def update(self):
        responses = Response.all(self)
        counts = Counter([r.utterance for r in responses])
        if not counts:
            return
        _, topcnt = counts.most_common(1)[0]
        self.success = topcnt

    def complete(self):
        assert self.success is not None
        self.close("COMPLETED")
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_turn = models.IntegerField()


class Response(BaseResponseModel):
    trial = models.Link(Trial)
    player = models.Link(Player)

    utterance = models.StringField()


def set_payoff(group: Group, iteround: Round):
    for player in group.get_players():
        player.total_score = iteround.total_score
        player.payoff = player.total_score.to_real_world_currency(player.session)  # type: ignore


def custom_export_responses(_):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
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
        "trial.success",
        "trial.score",
        #
        "response.iteration",
        "response.utterance",
    ]

    for response in Response.totall():
        trial = response.trial
        iteround = trial.iteround
        player = response.player

        yield [
            player.session.code,
            player.session.label,
            player.participant.code,
            player.participant.label,
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
            trial.success,
            trial.score,
            #
            response.iteration,
            response.utterance,
        ]
