import random

from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.itermodels import BaseRoundModel, BaseTrialModel, BaseResponseModel
from _stuff.dictprop import dictprop
from _stuff.layout import layoutdict, derange

from .conf import C, Points


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = database.StringField()
    disclosure = database.StringField()
    layout = database.StringField()
    total_score = database.DecimalField(unit=Points, initial=0)


class Round(BaseRoundModel):
    player: Player = database.Link(Player)
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

    label_a = database.StringField()
    label_b = database.StringField()
    label_c = database.StringField()
    labels = dictprop("label_", "ABC")

    param_x = database.FloatField()
    param_y = database.FloatField()
    param_z = database.FloatField()
    param_std = database.FloatField()
    params = dictprop("param_", ('x', 'y', 'z', 'std'))

    score = database.DecimalField(unit=Points, initial=0)

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    @property
    def disclosure(self) -> str:
        return self.iteround.player.disclosure

    @property
    def layout(self) -> dict[int, str]:
        return layoutdict(self.iteround.player.layout)

    def init(self, **kwargs):
        config = C.PARAMS[self.condition]
        self.param_x = config['x'].sample()
        self.param_y = config['y'].sample()
        self.param_z = config['z']
        self.param_std = config['std']

        labels = derange(self.layout, C.LABELS)
        self.label_a = labels["A"]
        self.label_b = labels["B"]
        self.label_c = labels["C"]

    def update(self):
        response = Response.last(self, stage='FINAL')
        self.score = response.result if response else None

    def complete(self):
        self.close('COMPLETED')
        assert self.score is not None
        self.iteround.total_score += self.score

    progress_samples = database.IntegerField()


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    player: Player = database.Link(Player)
    stage = database.StringField()

    response_time = database.IntegerField()
    button = database.IntegerField()
    choice = database.StringField()

    outcome_a = database.DecimalField(unit=Points)
    outcome_b = database.DecimalField(unit=Points)
    outcome_c = database.DecimalField(unit=Points)
    outcomes = dictprop("outcome_", "ABC")

    result = database.DecimalField(unit=Points)

    def evaluate(self):
        assert self.choice is not None
        params = self.trial.params
        x = params['x']
        y = params['y']
        z = params['z']

        c = z + random.gauss(0, params['std'])
        a = c + x
        b = c + y

        disclosure = self.trial.disclosure
        if disclosure == 'FULL' or (disclosure == 'FINAL' and self.stage == 'FINAL'):
            self.outcome_a = Points(a)
            self.outcome_b = Points(b)
            self.outcome_c = Points(c)
        if disclosure == 'CHOICE' or (disclosure == 'FINAL' and self.stage == 'SAMPLING'):
            self.outcome_a = Points(a) if self.choice == 'A' else None
            self.outcome_b = Points(b) if self.choice == 'B' else None
            self.outcome_c = Points(c) if self.choice == 'C' else None

        self.result = self.outcomes[self.choice]


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
        "layout",
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
        "trial.param.x",
        "trial.param.y",
        "trial.param.z",
        "trial.param.std",
        "trial.label.A",
        "trial.label.B",
        "trial.label.C",
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
            player.layout,
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
            trial.param_x,
            trial.param_y,
            trial.param_z,
            trial.param_std,
            trial.label_a,
            trial.label_b,
            trial.label_c,
            trial.score,
        ]


def custom_export_responses(_: list[Player]):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
        "condition",
        "layout",
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
            player.layout,
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
