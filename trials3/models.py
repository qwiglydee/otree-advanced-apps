import random

from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.itermodels import BaseRoundModel, BaseTrialModel, BaseResponseModel
from _stuff.dictprop import dictprop

from .conf import C, Points


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = database.StringField()
    total_score = database.DecimalField(unit=Points, initial=0)


class Round(BaseRoundModel):
    player: Player = database.Link(Player)
    ispractice = database.BooleanField()
    total_score = database.DecimalField(unit=Points, initial=0)

    @property
    def is_practice(self) -> bool:
        return self.pagename == 'Practice'

    def init(self, **kwargs):
        pass

    def update(self):
        pass

    progress_trials = database.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = database.Link(Round)

    task = database.StringField()
    truth = database.StringField()

    option_1 = database.StringField()
    option_2 = database.StringField()
    option_3 = database.StringField()
    options = dictprop('option_', '123')

    strategy = database.StringField()
    success = database.IntegerField()
    score = database.DecimalField(unit=Points, initial=0)

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    def init(self, **kwargs):
        config = C.NUMBERS[self.condition]
        num1, num2 = config.samples(2)
        result = num1 + num2

        self.task = f"{num1} + {num2}"
        self.truth = str(result)

        options = [result, result + 10, result - 10]
        random.shuffle(options)

        self.option_1 = str(options[0])
        self.option_2 = str(options[1])
        self.option_3 = str(options[2])

    def update(self):
        response = Response.last(self, stage='DECISION')
        self.strategy = response.decision if response else None
        response = Response.last(self, stage='ANSWER')
        self.success = response.correct if response else None

    def complete(self):
        self.close('COMPLETED')
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_retries = database.IntegerField()
    progress_stage = database.StringField()


class Response(BaseResponseModel):
    """Both for decisions and answers"""
    trial: Trial = database.Link(Trial)
    player: Player = database.Link(Player)
    stage = database.StringField()
    response_time = database.IntegerField()

    decision = database.StringField()
    button = database.StringField()
    answer = database.StringField()
    correct = database.BooleanField()

    def evaluate(self):
        if self.stage == 'ANSWER':
            assert self.answer is not None
            self.correct = self.answer == self.trial.truth


def set_payoff(player: Player, iteround: Round):
    if iteround.is_practice:
        return
    player.total_score = iteround.total_score
    player.payoff = player.total_score


def custom_export_trials(_: list[Player]):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
        "condition",
        #
        "iteround.pagename",
        "iteround.is_practice",
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
        "trial.task",
        "trial.truth",
        "trial.option_1",
        "trial.option_2",
        "trial.option_3",
        "trial.strategy",
        "trial.success",
        "trial.score",
        "trial.retries",
    ]

    for trial in Trial.objects_filter().order_by('iteround_id', 'iteration'):
        iteround: Round = trial.iteround
        player: Player = iteround.player
        session: Session = player.session
        participant: Participant = player.participant

        yield [
            session.code,
            session.label,
            participant.code,
            participant.label,
            player.condition,
            #
            iteround.pagename,
            iteround.is_practice,
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
            trial.task,
            trial.truth,
            trial.option_1,
            trial.option_2,
            trial.option_3,
            trial.strategy,
            trial.success,
            trial.score,
            trial.progress_retries
        ]


def custom_export_responses(_: list[Player]):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
        "condition",
        #
        "iteround.pagename",
        "iteround.is_practice",
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
        "trial.task",
        "trial.truth",
        "trial.option_1",
        "trial.option_2",
        "trial.option_3",
        "trial.strategy",
        "trial.success",
        "trial.score",
        "trial.retries",
        #
        "response.iteration",
        "response.stage",
        "response.time",
        "response.decision",
        "response.button",
        "response.answer",
        "response.correct",
    ]

    for response in Response.objects_filter().order_by('trial_id', 'iteration'):
        trial: Trial = response.trial
        iteround: Round = trial.iteround
        player: Player = iteround.player
        session: Session = player.session
        participant: Participant = player.participant

        yield [
            session.code,
            session.label,
            participant.code,
            participant.label,
            player.condition,
            #
            iteround.pagename,
            iteround.is_practice,
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
            trial.task,
            trial.truth,
            trial.option_1,
            trial.option_2,
            trial.option_3,
            trial.strategy,
            trial.success,
            trial.score,
            trial.progress_retries,
            #
            response.iteration,
            response.stage,
            response.response_time,
            response.decision,
            response.button,
            response.answer,
            response.correct,
        ]
