from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.iterating import BaseRoundModel, BaseTrialModel, BaseResponseModel
from _stuff.dictprop import dictproperty

from .const import C


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = database.StringField()
    total_score = database.IntegerField(initial=0)


class Round(BaseRoundModel):
    player: Player = database.Link(Player)
    ispractice = database.BooleanField()
    total_score = database.IntegerField(initial=0)

    @property
    def condition(self) -> str:
        return self.player.condition

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

    progress_trials = database.IntegerField(initial=0)


class Trial(BaseTrialModel):
    iteround: Round = database.Link(Round)

    task = database.StringField()
    truth = database.StringField()

    option_1 = database.StringField()
    option_2 = database.StringField()
    option_3 = database.StringField()
    options = dictproperty('option_', '123')

    success = database.IntegerField()
    score = database.IntegerField(initial=0)

    def init(self, **kwargs):
        if not kwargs:
            # skip auto-init
            return

        self.task = kwargs['task']
        self.truth = kwargs['truth']
        self.option_1 = kwargs['option_1']
        self.option_2 = kwargs['option_2']
        self.option_3 = kwargs['option_3']

    def update(self):
        """Update something after a response"""
        response = Response.last(self)
        self.success = response and response.correct

    def complete(self):
        super().complete()
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_retries = database.IntegerField(initial=0)


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    player: Player = database.Link(Player)

    response_time = database.IntegerField()
    choice = database.IntegerField()
    answer = database.StringField()
    correct = database.BooleanField()

    @classmethod
    def respond(cls, trial: Trial, player: Player, response_time: int, choice: int):
        response = cls.create_next(trial, player)
        response.response_time = response_time
        response.choice = choice
        response.answer = trial.options[choice]
        response.correct = response.answer == trial.truth
        return response


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
        "iteround.progress_trials",
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
        "response.choice",
        "response.answer",
        "response.correct",

    ]

    for trial in Trial.objects_filter():
        iteround: Round = trial.iteround
        player: Player = iteround.player
        session: Session = player.session
        participant: Participant = player.participant

        fields = [
            session.code,
            session.label,
            participant.code,
            participant.label,
            #
            iteround.condition,
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

        yield fields

        responses = Response.list(trial=trial)
        for resp in responses:
            yield fields + [
                resp.iteration,
                resp.response_time,
                resp.choice,
                resp.answer,
                resp.correct,
            ]
