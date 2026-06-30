import random

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models

from _extras.keyprop import dict_getter, key_getter
from _extras.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from _extras.layout import derange, layoutdict
from _extras.score import score_to_currency

from units import Points

from .conf import C


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()
    disclosure = models.StringField()
    layout = models.StringField()
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

    label_a = models.StringField()
    label_b = models.StringField()
    label_c = models.StringField()
    get_labels = dict_getter("label_", ("A", "B", "C"))
    get_label = key_getter("label_")

    param_x = models.FloatField()
    param_y = models.FloatField()
    param_z = models.FloatField()
    param_std = models.FloatField()

    score = models.DecimalField(unit=Points)

    @property
    def layout(self) -> dict[int, str]:
        return layoutdict(self.iteround.player.layout)

    def init(self):
        config = C.PARAMS[self.iteround.player.condition]
        self.param_x = config["x"].sample()
        self.param_y = config["y"].sample()
        self.param_z = config["z"]
        self.param_std = config["std"]

        labels = derange(self.layout, C.LABELS)
        self.label_a = labels["A"]
        self.label_b = labels["B"]
        self.label_c = labels["C"]

    def update(self):
        responded = Response.last(self, stage="FINALIZING")
        if responded:
            assert responded.result is not None
            self.score = responded.result

    def complete(self):
        assert self.score is not None
        self.close("COMPLETED")
        self.iteround.total_score += self.score

    progress_responses = models.IntegerField(initial=0)
    progress_samples = models.IntegerField(initial=0)


class Response(BaseResponseModel):
    trial: Trial = models.Link(Trial)
    player: Player = models.Link(Player)
    stage = models.StringField()

    response_time = models.IntegerField()
    button = models.IntegerField()
    choice = models.StringField()

    outcome_a = models.DecimalField(unit=Points)
    outcome_b = models.DecimalField(unit=Points)
    outcome_c = models.DecimalField(unit=Points)
    get_outcomes = dict_getter("outcome_", ("A", "B", "C"))
    get_outcome = key_getter("outcome_")

    result = models.DecimalField(unit=Points)

    def evaluate(self):
        assert self.choice is not None
        x = self.trial.param_x
        y = self.trial.param_y
        z = self.trial.param_z
        std = self.trial.param_std

        c = z + random.gauss(0, std)
        a = c + x
        b = c + y

        disclosure = self.player.disclosure
        if disclosure == "FULL":
            self.outcome_a = Points(a)
            self.outcome_b = Points(b)
            self.outcome_c = Points(c)
        if disclosure == "CHOICE":
            self.outcome_a = Points(a) if self.choice == "A" else None
            self.outcome_b = Points(b) if self.choice == "B" else None
            self.outcome_c = Points(c) if self.choice == "C" else None

        self.result = self.get_outcome(self.choice)


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
        "response.stage",
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
            response.stage,
            response.response_time,
            response.button,
            response.choice,
            response.outcome_a,
            response.outcome_b,
            response.outcome_c,
            response.result,
        ]
