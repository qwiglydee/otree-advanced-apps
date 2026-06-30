from otree.api import BaseGroup, BasePlayer, BaseSubsession, models

from _extras.keyprop import dict_getter, key_getter
from _extras.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from _extras.score import score_to_currency

from units import Points

from .conf import C


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()
    total_score = models.DecimalField(unit=Points, initial=0)


class Round(BaseRoundModel):
    player: Player = models.Link(Player)

    total_score = models.DecimalField(unit=Points, initial=0)

    def init(self):
        pass

    def update(self):
        pass

    progress_trials = models.IntegerField(initial=0)


class Trial(BaseTrialModel):
    iteround: Round = models.Link(Round)

    taskid = models.StringField()
    question = models.StringField()
    truth = models.StringField()

    option_1 = models.StringField()
    option_2 = models.StringField()
    option_3 = models.StringField()
    get_options = dict_getter("option_", (1, 2, 3))
    get_option = key_getter("option_")

    success = models.BooleanField()
    score = models.DecimalField(unit=Points)

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
        responded = Response.last(self)
        if responded:
            self.success = responded.correct

    def complete(self):
        assert self.success is not None
        self.close("COMPLETED")
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_responses = models.IntegerField(initial=0)


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


def set_payoff(iteround: Round):
    player = iteround.player
    if iteround.pagename == "Main":
        player.total_score = iteround.total_score
        player.payoff = score_to_currency(player.total_score, player.session)  # type: ignore currency incompatibility


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
