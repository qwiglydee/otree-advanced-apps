from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant

from _stuff.iterating import BaseRoundModel, BaseTrialModel, BaseResponseModel
from _stuff.dictprop import dictproperty

from .source import sample_data
from .const import C, Points


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = database.StringField()
    total_score = database.DecimalField(unit=Points, initial=0)


class Round(BaseRoundModel):
    player: Player = database.Link(Player)
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
            self.player.total_score = self.total_score

    progress_trials = database.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = database.Link(Round)

    task = database.StringField()
    truth = database.StringField()

    option_1 = database.StringField()
    option_2 = database.StringField()
    option_3 = database.StringField()
    options = dictproperty('option_', '123')

    label_1 = database.StringField()
    label_2 = database.StringField()
    label_3 = database.StringField()
    labels = dictproperty('label_', '123')

    success = database.IntegerField()
    score = database.DecimalField(unit=Points, initial=0)

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    def init(self, **kwargs):
        if not kwargs:
            # skip auto-init
            return

        datarow = kwargs['datarow']

        self.task = datarow['task']
        self.truth = datarow['truth']
        self.option_1 = datarow['option_1']
        self.option_2 = datarow['option_2']
        self.option_3 = datarow['option_3']
        self.label_1 = datarow['label_1']
        self.label_2 = datarow['label_2']
        self.label_3 = datarow['label_3']

    def update(self):
        """Update something after a response"""
        response = Response.last(self)
        self.success = response and response.correct

    def complete(self):
        super().complete()
        self.score = C.SCORING[self.success]
        self.iteround.total_score += self.score

    progress_retries = database.IntegerField()


def generate_trials(count: int, player: Player, pagename: str, sourcedata: list[dict]):
    iteround = Round.create_new(pagename, player=player)
    data = sample_data(sourcedata, count, condition=player.condition, section=pagename)
    trials = Trial.create_many(iteround, count)
    for trial, datum in zip(trials, data, strict=True):
        trial.init(datarow=datum)


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    player: Player = database.Link(Player)

    response_time = database.IntegerField()
    button = database.StringField()
    answer = database.StringField()
    correct = database.BooleanField()

    def respond(self, response_time: int, button: str, answer: str):
        self.response_time = response_time
        self.button = button
        self.answer = answer
        self.correct = self.answer == self.trial.truth


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
        "trial.option_1",
        "trial.label_1",
        "trial.option_2",
        "trial.label_2",
        "trial.option_3",
        "trial.label_3",
        "trial.success",
        "trial.score",
        #
        "response.iteration",
        "response.time",
        "response.button",
        "response.answer",
        "response.correct",

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
            player.condition,
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
            trial.option_1,
            trial.label_1,
            trial.option_2,
            trial.label_2,
            trial.option_3,
            trial.label_3,
            trial.success,
            trial.score,
        ]

        yield fields

        responses = Response.list(trial=trial)
        for response in responses:
            yield fields + [
                response.iteration,
                response.response_time,
                response.button,
                response.answer,
                response.correct,
            ]
