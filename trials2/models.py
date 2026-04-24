from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer

from _stuff.iterating import BaseRoundModel, BaseTrialModel, BaseResponseModel

from .const import C


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    condition = database.StringField()
    total_score = database.IntegerField(initial=0)


class Player(BasePlayer):
    progress_round = database.IntegerField()
    progress_trial = database.IntegerField()


class Round(BaseRoundModel):
    group: Group = database.Link(Group)
    ispractice = database.BooleanField()
    total_score = database.IntegerField(initial=0)

    @property
    def condition(self) -> str:
        return self.group.condition

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

    progress_trials = database.IntegerField(initial=0)


class Trial(BaseTrialModel):
    iteround: Round = database.Link(Round)

    task = database.StringField()
    truth = database.StringField()
    success = database.IntegerField()
    score = database.IntegerField(initial=0)

    def init(self, **kwargs):
        condition = self.iteround.condition
        numbers = C.NUMBERS[condition]
        num1: int = numbers.sample()
        num2: int = numbers.sample()

        self.task = f"{num1} + {num2}"
        self.truth = str(num1 + num2)

    def update(self):
        self.success = Response.count(self, correct=True)

    def complete(self):
        super().complete()
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_stage = database.StringField()

    def start(self):
        super().start()
        self.progress_stage = C.STAGES[0]


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    stage = database.StringField()
    player: Player = database.Link(Player)

    response_time = database.IntegerField()
    answer = database.StringField()
    correct = database.BooleanField()

    @classmethod
    def respond(cls, trial: Trial, player: Player, response_time: int, answer: str):
        response = cls.create_next(trial, player, stage=trial.progress_stage)
        response.response_time = response_time
        response.answer = answer
        response.correct = response.answer == trial.truth
        return response

    @classmethod
    def all(cls, trial: Trial):
        # supporting multiple retries / subiterations
        players = trial.iteround.group.get_players()
        responses = [cls.last(trial, player=p) for p in players]
        return [r for r in responses if r is not None]
