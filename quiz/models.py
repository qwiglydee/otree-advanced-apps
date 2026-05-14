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

    taskid = database.StringField()
    question = database.StringField()
    truth = database.StringField()

    option_1 = database.StringField()
    option_2 = database.StringField()
    option_3 = database.StringField()
    options = dictprop('option_', "123")

    success = database.IntegerField()
    score = database.DecimalField(unit=Points, initial=0)

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    def init(self, **kwargs):
        if not kwargs:
            # skip auto-init
            return

        params = kwargs['conf']

        self.taskid = params['taskid']
        self.question = params['question']
        self.truth = params['answer']
        self.option_1 = params['option_1']
        self.option_2 = params['option_2']
        self.option_3 = params['option_3']

    def update(self):
        response = Response.last(self)
        self.success = response.correct if response else None

    def complete(self):
        self.close('COMPLETED')
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score


def create_trials(iteround: Round, data: list[dict]):
    count = len(data)
    trials = Trial.create_many(iteround, count)
    for trial, datum in zip(trials, data, strict=True):
        trial.init(conf=datum)


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    player: Player = database.Link(Player)

    response_time = database.IntegerField()
    button = database.StringField()
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
        "trial.taskid",
        "trial.question",
        "trial.truth",
        "trial.option_1",
        "trial.option_2",
        "trial.option_3",
        "trial.success",
        "trial.score",
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
            trial.taskid,
            trial.question,
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
        "trial.taskid",
        "trial.question",
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
            trial.taskid,
            trial.question,
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
