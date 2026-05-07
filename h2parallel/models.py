from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.iterating import BaseRoundModel, BaseTrialModel, BaseResponseModel

from .const import C, Points


def init_params(config):
    "Initialize trial parameters from config"
    return config.samples(2)


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
        params = init_params(C.NUMBERS[self.condition])
        [num1, num2] = params
        self.task = f"{num1} + {num2}"
        self.truth = str(num1 + num2)

    def update(self):
        responses = [r for r in Response.allast(self) if r.correct]
        self.success = len(responses)

    def complete(self):
        super().complete()
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    player: Player = database.Link(Player)

    response_time = database.IntegerField()
    answer = database.StringField()
    correct = database.BooleanField()

    def respond(self, response_time: int, answer: str):
        self.response_time = response_time
        self.answer = answer
        self.correct = self.answer == self.trial.truth

    @classmethod
    def allast(cls, trial: Trial):
        """Last responses of each player"""
        # supporting multiple retries / subiterations
        players = trial.iteround.group.get_players()
        responses = [cls.last(trial, player=p) for p in players]
        return [r for r in responses if r is not None]


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
    ]

    for trial in Trial.objects_filter().order_by('group_id', 'iteration'):
        iteround: Round = trial.iteround
        group: Group = iteround.group
        session: Session = group.session

        yield [
            session.code,
            session.label,
            None,
            None,
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
        #
        "player.role",
        "response.iteration",
        "response.time",
        "response.answer",
        "response.correct",
    ]

    for response in Response.objects_filter().order_by('trial_id', 'iteration'):
        trial: Trial = response.trial
        iteround: Round = trial.iteround
        group: Group = iteround.group
        player: Player = response.player
        session: Session = player.session
        participant: Participant = player.participant

        yield [
            session.code,
            session.label,
            participant.code,
            participant.label,
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
            #
            player.role,
            response.iteration,
            response.response_time,
            response.answer,
            response.correct,
        ]
