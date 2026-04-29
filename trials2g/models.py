from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.iterating import BaseRoundModel, BaseTrialModel, BaseResponseModel

from .const import C, Points


def sample_params(numbers):
    num1 = numbers.sample()
    num2 = numbers.sample()
    return num1, num2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    condition = database.StringField()
    total_score = database.DecimalField(unit=Points, initial=0)


class Player(BasePlayer):
    progress_round = database.IntegerField()
    progress_trial = database.IntegerField()


class Round(BaseRoundModel):
    group: Group = database.Link(Group)
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
            self.group.total_score = self.total_score

    progress_trials = database.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = database.Link(Round)

    task = database.StringField()
    truth = database.StringField()
    success = database.IntegerField()
    score = database.DecimalField(unit=Points, initial=0)

    @property
    def condition(self) -> str:
        return self.iteround.group.condition

    def init(self, **kwargs):
        num1, num2 = sample_params(C.NUMBERS[self.condition])
        self.task = f"{num1} + {num2}"
        self.truth = str(num1 + num2)

    def update(self):
        self.success = Response.count(self, correct=True)

    def complete(self):
        super().complete()
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_stage = database.StringField()


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    stage = database.StringField()
    player: Player = database.Link(Player)

    response_time = database.IntegerField()
    answer = database.StringField()
    correct = database.BooleanField()

    def respond(self, response_time: int, answer: str):
        self.response_time = response_time
        self.answer = answer
        self.correct = self.answer == self.trial.truth

    @classmethod
    def all(cls, trial: Trial):
        # supporting multiple retries / subiterations
        players = trial.iteround.group.get_players()
        responses = [cls.last(trial, player=p) for p in players]
        return [r for r in responses if r is not None]


def custom_export_trials(_: list[Player]):
    yield [
        "session.code",
        "session.label",
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
        #
        "participant.code",
        "participant.label",
        "player.role",
        #
        "response.iteration",
        "response.stage",
        "response.time",
        "response.answer",
        "response.correct",

    ]

    for trial in Trial.objects_filter():
        iteround: Round = trial.iteround
        group: Group = iteround.group
        session: Session = group.session

        fields = [
            session.code,
            session.label,
            group.condition,
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
        ]

        yield fields

        responses = Response.list(trial=trial)
        for response in responses:
            player: Player = response.player
            participant: Participant = player.participant
            yield fields + [
                participant.code,
                participant.label,
                player.role,
                #
                response.iteration,
                response.stage,
                response.response_time,
                response.answer,
                response.correct,
            ]
