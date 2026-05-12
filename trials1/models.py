from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.itermodels import BaseRoundModel, BaseTrialModel, BaseResponseModel

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

    def update(self):
        response = Response.last(self)
        self.success = response.correct if response else None

    def complete(self):
        self.close('COMPLETED')
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_retries = database.IntegerField()


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    player: Player = database.Link(Player)

    response_time = database.IntegerField()
    answer = database.StringField()
    correct = database.BooleanField()

    def evaluate(self):
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
        "trial.success",
        "trial.score",
        "trial.retries",
        #
        "response.iteration",
        "response.time",
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
            trial.success,
            trial.score,
            trial.progress_retries,
            #
            response.iteration,
            response.response_time,
            response.answer,
            response.correct,
        ]
