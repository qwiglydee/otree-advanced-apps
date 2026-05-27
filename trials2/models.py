import random

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models

from _extras.keyprop import dict_getter, key_getter
from _extras.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from units import Points

from .conf import C


def PointsField(**kwargs):
    return models.DecimalField(unit=Points, **kwargs)  # type: ignore internal incompatibility


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()
    total_score = PointsField(initial=0)


class Round(BaseRoundModel):
    player: Player = models.Link(Player)
    ispractice = models.BooleanField()
    total_score = PointsField(initial=0)

    def init(self):
        pass

    def update(self):
        pass

    progress_trials = models.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = models.Link(Round)

    task = models.StringField()
    truth = models.StringField()

    option_1 = models.StringField()
    option_2 = models.StringField()
    option_3 = models.StringField()
    get_options = dict_getter("option_", (1, 2, 3))
    get_option = key_getter("option_")

    success = models.BooleanField()
    score = PointsField(initial=None)

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    def init(self):
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
        response = Response.last(self)
        if response:
            self.success = response.correct

    def complete(self):
        assert self.success is not None
        self.close("COMPLETED")
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_retries = models.IntegerField()


class Response(BaseResponseModel):
    trial: Trial = models.Link(Trial)
    player: Player = models.Link(Player)

    response_time = models.IntegerField()
    button = models.IntegerField()
    answer = models.StringField()
    correct = models.BooleanField()

    def evaluate(self):
        assert self.answer is not None
        self.correct = self.answer == self.trial.truth


def set_payoff(player: Player, iteround: Round):
    if iteround.pagename == "Main":
        player.total_score = iteround.total_score
        player.payoff = player.total_score.to_real_world_currency(player.session)  # type: ignore


def custom_export_trials(_):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
        "condition",
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
        "trial.task",
        "trial.truth",
        "trial.option_1",
        "trial.option_2",
        "trial.option_3",
        "trial.success",
        "trial.score",
        "trial.retries",
    ]

    for trial in Trial.totall():
        iteround = trial.iteround
        player = iteround.player

        yield [
            player.session.code,
            player.session.label,
            player.participant.code,
            player.participant.label,
            player.condition,
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
            trial.task,
            trial.truth,
            trial.option_1,
            trial.option_2,
            trial.option_3,
            trial.success,
            trial.score,
            trial.progress_retries,
        ]


def custom_export_responses(_):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
        "condition",
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
        "trial.task",
        "trial.truth",
        "trial.option_1",
        "trial.option_2",
        "trial.option_3",
        "trial.success",
        "trial.score",
        "trial.retries",
        #
        "response.iteration",
        "response.time",
        "response.button",
        "response.answer",
        "response.correct",
    ]

    for response in Response.totall():
        trial = response.trial
        iteround = trial.iteround
        player = iteround.player

        yield [
            player.session.code,
            player.session.label,
            player.participant.code,
            player.participant.label,
            player.condition,
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
            trial.task,
            trial.truth,
            trial.option_1,
            trial.option_2,
            trial.option_3,
            trial.success,
            trial.score,
            trial.progress_retries,
            #
            response.iteration,
            response.response_time,
            response.button,
            response.answer,
            response.correct,
        ]
