import random

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models

from _stuff.dictprop import dictprop
from _stuff.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from _stuff.layout import derange, layoutdict
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
    disclosure = models.StringField()
    layout = models.StringField()
    total_score = PointsField(initial=0)


class Round(BaseRoundModel):
    player: Player = models.Link(Player)
    total_score = PointsField(initial=0)

    def init(self):
        pass

    def update(self):
        pass

    progress_trials = models.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = models.Link(Round)

    label_a = models.StringField()
    label_b = models.StringField()
    label_c = models.StringField()
    labels = dictprop("label_", "ABC")

    param_x = models.FloatField()
    param_y = models.FloatField()
    param_z = models.FloatField()
    param_std = models.FloatField()
    params = dictprop("param_", ("x", "y", "z", "std"))

    score = PointsField(initial=None)

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    @property
    def disclosure(self) -> str:
        return self.iteround.player.disclosure

    @property
    def layout(self) -> dict[int, str]:
        return layoutdict(self.iteround.player.layout)

    def init(self):
        config = C.PARAMS[self.condition]
        self.param_x = config["x"].sample()
        self.param_y = config["y"].sample()
        self.param_z = config["z"]
        self.param_std = config["std"]

        labels = derange(self.layout, C.LABELS)
        self.label_a = labels["A"]
        self.label_b = labels["B"]
        self.label_c = labels["C"]

    def update(self):
        response = Response.last(self)
        if response:
            self.score = response.result

    def complete(self):
        assert self.score is not None
        self.close("COMPLETED")
        self.iteround.total_score += self.score


class Response(BaseResponseModel):
    trial: Trial = models.Link(Trial)
    player: Player = models.Link(Player)

    response_time = models.IntegerField()
    button = models.IntegerField()
    choice = models.StringField()

    outcome_a = PointsField()
    outcome_b = PointsField()
    outcome_c = PointsField()
    outcomes = dictprop("outcome_", "ABC")

    result = PointsField()

    def evaluate(self):
        assert self.choice is not None
        params = self.trial.params
        x = params["x"]
        y = params["y"]
        z = params["z"]

        c = Points(z + random.gauss(0, params["std"]))
        a = Points(c + x)
        b = Points(c + y)

        disclosure = self.trial.disclosure
        if disclosure == "FULL":
            self.outcome_a = a
            self.outcome_b = b
            self.outcome_c = c
        if disclosure == "CHOICE":
            self.outcome_a = a if self.choice == "A" else None
            self.outcome_b = b if self.choice == "B" else None
            self.outcome_c = c if self.choice == "C" else None

        self.result = self.outcomes[self.choice]


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
        "layout",
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
        "trial.param.x",
        "trial.param.y",
        "trial.param.z",
        "trial.param.std",
        "trial.label.A",
        "trial.label.B",
        "trial.label.C",
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
            player.layout,
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
            trial.param_x,
            trial.param_y,
            trial.param_z,
            trial.param_std,
            trial.label_a,
            trial.label_b,
            trial.label_c,
            trial.score,
        ]


def custom_export_responses(_):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
        "condition",
        "layout",
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
        "trial.param.x",
        "trial.param.y",
        "trial.param.z",
        "trial.param.std",
        "trial.label.A",
        "trial.label.B",
        "trial.label.C",
        "trial.score",
        #
        "response.iteration",
        "response.response_time",
        "response.button",
        "response.choice",
        "response.outcome.A",
        "response.outcome.B",
        "response.outcome.C",
        "response.result",
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
            player.layout,
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
            trial.param_x,
            trial.param_y,
            trial.param_z,
            trial.param_std,
            trial.label_a,
            trial.label_b,
            trial.label_c,
            trial.score,
            #
            response.iteration,
            response.response_time,
            response.button,
            response.choice,
            response.outcome_a,
            response.outcome_b,
            response.outcome_c,
            response.result,
        ]
