from collections import Counter

from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.itermodels import BaseRoundModel, BaseTrialModel, BaseResponseModel

from .conf import C, Points


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    total_score = database.DecimalField(unit=Points, initial=0)
    progress_round = database.IntegerField()
    progress_trial = database.IntegerField()


class Round(BaseRoundModel):
    group: Group = database.Link(Group)
    total_score = database.DecimalField(unit=Points, initial=0)

    def init(self, **kwargs):
        pass

    def update(self):
        pass

    progress_trials = database.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = database.Link(Round)

    success = database.IntegerField()
    score = database.DecimalField(unit=Points, initial=0)

    def init(self, **kwargs):
        pass

    def update(self):
        responses = Response.group_last(self, self.iteround.group)
        counts = Counter([r.utterance for r in responses])
        if not counts:
            return
        _, topcnt = counts.most_common(1)[0]
        self.success = topcnt

    def complete(self):
        assert self.success is not None
        self.close('COMPLETED')
        self.score = C.SCORING.get(self.success, 0)
        self.iteround.total_score += self.score

    progress_turn = database.IntegerField()


class Response(BaseResponseModel):
    trial = database.Link(Trial)
    player = database.Link(Player)

    utterance = database.StringField()


def set_payoff(group: Group, iteround: Round):
    for player in group.get_players():
        player.total_score = iteround.total_score
        player.payoff = player.total_score


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

    for response in Response.objects_filter().order_by('trial_id', 'iteration'):
        trial: Trial = response.trial
        iteround: Round = trial.iteround
        player: Player = response.player
        session: Session = player.session
        participant: Participant = player.participant

        yield [
            session.code,
            session.label,
            participant.code,
            participant.label,
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
