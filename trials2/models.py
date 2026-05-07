import random

from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.iterating import BaseRoundModel, BaseTrialModel, BaseResponseModel
from _stuff.dictprop import dictproperty

from .const import C, Points


def init_params(config):
    "Initialize trial parameters from config"
    num1, num2 = config.samples(2)
    result = num1 + num2
    options = [result, result + 10, result - 10]
    random.shuffle(options)
    return {
        'task': f"{num1} + {num2}",
        'truth': str(result),
        'options': [str(v) for v in options]
    }


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
        """Init sometthing when created"""
        pass

    def update(self):
        """Update something when started or after a trial completed"""
        pass

    def complete(self):
        super().complete()
        if not self.is_practice:
            self.player.total_score = self.total_score

    progress_trials = database.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = database.Link(Round)

    task = database.StringField()
    truth = database.StringField()

    option_1 = database.StringField()
    option_2 = database.StringField()
    option_3 = database.StringField()
    options = dictproperty('option_', '123')

    success = database.IntegerField()
    score = database.DecimalField(unit=Points, initial=0)

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    def init(self, **kwargs):
        params = init_params(C.NUMBERS[self.condition])
        self.task = params['task']
        self.truth = params['truth']
        self.option_1 = params['options'][0]
        self.option_2 = params['options'][1]
        self.option_3 = params['options'][2]

    def update(self):
        """Update something after a response"""
        response = Response.last(self)
        self.success = response and response.correct

    def complete(self):
        super().complete()
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_retries = database.IntegerField()


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    player: Player = database.Link(Player)

    response_time = database.IntegerField()
    button = database.StringField()
    answer = database.StringField()
    correct = database.BooleanField()

    def respond(self, response_time: int, button: str, answer: str):
        self.response_time = response_time
        self.button = button
        self.answer = answer
        self.correct = self.answer == self.trial.truth


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
        "trial.success",
        "trial.score",
    ]

    for trial in Trial.objects_filter().order_by('player_id', 'iteration'):
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
            trial.success,
            trial.score,
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
        "trial.success",
        "trial.score",
        #
        "response.iteration",
        "response.time",
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
            trial.success,
            trial.score,
            #
            response.iteration,
            response.response_time,
            response.button,
            response.answer,
            response.correct,
        ]
