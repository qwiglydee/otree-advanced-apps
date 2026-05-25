from otree.api import BaseGroup, BasePlayer, BaseSubsession, models

from _extras.keyprop import dict_getter
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

    taskid = models.StringField()
    question = models.StringField()
    truth = models.StringField()

    option_1 = models.StringField()
    option_2 = models.StringField()
    option_3 = models.StringField()
    get_options = dict_getter("option_", (1, 2, 3))

    success = models.IntegerField()
    score = PointsField(initial=None)

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    def init(self, **kwargs):
        if not kwargs:
            # skip auto-init
            return

        params = kwargs["conf"]

        self.taskid = params["taskid"]
        self.question = params["question"]
        self.truth = params["answer"]
        self.option_1 = params["option_1"]
        self.option_2 = params["option_2"]
        self.option_3 = params["option_3"]

    def update(self):
        response = Response.last(self)
        if response:
            self.success = response.correct

    def complete(self):
        assert self.success is not None
        self.close("COMPLETED")
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score


def create_trials(iteround: Round, data: list[dict]):
    count = len(data)
    trials = Trial.create_many(iteround, count)
    for trial, datum in zip(trials, data, strict=True):
        trial.init(conf=datum)


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
        "trial.taskid",
        "trial.question",
        "trial.truth",
        "trial.option_1",
        "trial.option_2",
        "trial.option_3",
        "trial.success",
        "trial.score",
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
            trial.taskid,
            trial.question,
            trial.truth,
            trial.option_1,
            trial.option_2,
            trial.option_3,
            trial.success,
            trial.score,
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
