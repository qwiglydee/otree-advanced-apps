import random

from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.iterating import BaseRoundModel, BaseTrialModel, BaseResponseModel
from _stuff.layout import layoutdict, derange
from _stuff.dictprop import dictproperty

from .const import C, Points


def sample_params(params: dict):
    "Realize trial parameters from conf PARAMS"
    return {
        'x': params['x'].sample(),
        'y': params['y'].sample(),
        'z': params['z'],
        'std': params['std']
    }


def evaluate_outcomes(choice: str, x: float, y: float, z: float, std: float):
    "Realize outcomes for given params"
    a = z + random.gauss(x, std)
    b = z + random.gauss(y, std)
    c = z + random.gauss(0, std)
    return {
        'A': Points(a),
        'B': Points(b),
        'C': Points(c),
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = database.StringField()
    layout = database.StringField()
    total_score = database.DecimalField(unit=Points, initial=0)


class Round(BaseRoundModel):
    player: Player = database.Link(Player)
    total_score = database.DecimalField(unit=Points, initial=0)

    @property
    def is_practice(self):
        return self.pagename == 'Practice'

    def init(self, **kwargs):
        pass

    def update(self):
        pass

    def complete(self):
        super().complete()
        if not self.is_practice:
            self.player.total_score = self.total_score

    progress_trials = database.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = database.Link(Round)

    label_a = database.StringField()
    label_b = database.StringField()
    label_c = database.StringField()
    labels = dictproperty("label_", "ABC")

    param_x = database.FloatField()
    param_y = database.FloatField()
    param_z = database.FloatField()
    param_std = database.FloatField()

    score = database.DecimalField(unit=Points, initial=0)

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    @property
    def layout(self) -> dict[int, str]:
        return layoutdict(self.iteround.player.layout)

    def init(self, **kwargs):
        labels = derange(self.layout, C.LABELS)
        self.label_a = labels["A"]
        self.label_b = labels["B"]
        self.label_c = labels["C"]

        params = sample_params(C.PARAMS[self.condition])
        self.param_x = params['x']
        self.param_y = params['y']
        self.param_z = params['z']
        self.param_std = params['std']

    def update(self):
        pass

    def complete(self):
        super().complete()
        response = Response.last(self, stage='FINAL')
        assert response
        self.score = response.result
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
    outcomes = dictproperty("outcome_", "ABC")

    result = database.DecimalField(unit=Points)

    def respond(self, response_time: int, button: int, choice: str):
        self.response_time = response_time
        self.button = button
        self.choice = choice

        outcomes = evaluate_outcomes(
            choice,
            self.trial.param_x,
            self.trial.param_y,
            self.trial.param_z,
            self.trial.param_std,
        )
        self.outcome_a = outcomes['A']
        self.outcome_b = outcomes['B']
        self.outcome_c = outcomes['C']

        self.result = outcomes[choice]


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
        "trial.label.A",
        "trial.label.B",
        "trial.label.C",
        "trial.param.x",
        "trial.param.y",
        "trial.param.z",
        "trial.score",
        #
        "response.iteration",
        "response.stage",
        "response.response_time",
        "response.outcome.A",
        "response.outcome.B",
        "response.outcome.C",
        "response.button",
        "response.choice",
        "response.result"
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
            player.condition,
            player.layout,
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
            trial.label_a,
            trial.label_b,
            trial.label_c,
            trial.param_x,
            trial.param_y,
            trial.param_z,
            trial.score,
        ]

        yield fields

        responses = Response.list(trial=trial)
        for response in responses:
            yield fields + [
                response.iteration,
                response.stage,
                response.response_time,
                response.outcome_a,
                response.outcome_b,
                response.outcome_c,
                response.button,
                response.choice,
                response.result,
            ]
