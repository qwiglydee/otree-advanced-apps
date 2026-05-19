from otree.api import BaseGroup, BasePlayer, BaseSubsession, models, widgets

from _stuff.dictprop import dictprop
from _stuff.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from units import Points

from .conf import C, config_condition


def PointsField():
    return models.DecimalField(unit=Points, initial=0)  # type: ignore internal incompatibility


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    condition = models.StringField()


class Player(BasePlayer):
    age = models.IntegerField()
    gender = models.StringField(choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], widget=widgets.RadioSelect)

    total_score = PointsField()

    progress_round = models.IntegerField()
    progress_trial = models.IntegerField()

    @property
    def condition(self) -> str:
        return self.group.condition  # type: ignore


class Round(BaseRoundModel):
    group: Group = models.Link(Group)

    total_score_p = PointsField()
    total_score_r = PointsField()
    total_scores = dictprop("total_score_", ("P", "R"))

    def init(self):
        pass

    def update(self):
        pass

    autorespond_role = models.StringField()
    progress_trials = models.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = models.Link(Round)

    endowment = PointsField()
    proposal = PointsField()
    decision = models.StringField(choices=C.DECISIONS)

    score_p = PointsField()
    score_r = PointsField()
    scores = dictprop("score_", ("P", "R"))

    @property
    def condition(self) -> str:
        return self.iteround.group.condition

    def init(self):
        self.endowment = C.ENDOWMENT[self.condition]

    def update(self):
        proposed = Response.last(self, stage="PROPOSING")
        self.proposal = proposed.p_proposal if proposed else None
        decided = Response.last(self, stage="DECIDING")
        self.decision = decided.r_decision if decided else None

    def complete(self):
        self.close("COMPLETED")
        assert self.proposal is not None
        if self.decision == "ACCEPT":
            self.score_p = self.endowment - self.proposal
            self.score_r = self.proposal
            self.iteround.total_score_p += self.score_p
            self.iteround.total_score_r += self.score_r

    progress_stage = models.StringField()


class Response(BaseResponseModel):
    trial: Trial = models.Link(Trial)
    stage = models.StringField()
    player: Player = models.Link(Player)
    autoresponded = models.BooleanField(initial=False)

    response_time = models.IntegerField()
    p_proposal = PointsField()
    r_decision = models.StringField(choices=C.DECISIONS)


def setup_group(group: Group):
    group.condition = config_condition(group.session)


def set_payoff(group: Group, iteround: Round):
    scores = iteround.total_scores
    for player in group.get_players():
        player.total_score = scores[player.role]
        if player.participant.status != "dropout":
            player.payoff = player.total_score.to_real_world_currency(player.session)  # type: ignore


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
        "iteround.total_score.P",
        "iteround.total_score.R",
        #
        "trial.iteration",
        "trial.status",
        "trial.completion",
        "trial.processing_time",
        "trial.endowment",
        "trial.proposal",
        "trial.decision",
        "trial.score.P",
        "trial.score.R",
        #
        "response.iteration",
        "response.stage",
        "player.role",
        "response.autoresponded",
        "response.response_time",
        "response.proposal",
        "response.decision",
    ]

    for response in Response.totall():
        trial = response.trial
        iteround = trial.iteround
        group = iteround.group
        player = response.player

        yield [
            player.session.code,
            player.session.label,
            player.participant.code,
            player.participant.label,
            group.condition,
            #
            iteround.pagename,
            iteround.status,
            iteround.completion,
            f"{iteround.processing_time:.01f}" if iteround.processing_time else None,
            iteround.progress_trials,
            iteround.total_score_p,
            iteround.total_score_r,
            #
            trial.iteration,
            trial.status,
            trial.completion,
            f"{trial.processing_time:.01f}" if trial.processing_time else None,
            trial.endowment,
            trial.proposal,
            trial.decision,
            trial.score_p,
            trial.score_r,
            #
            response.iteration,
            response.stage,
            player.role,
            response.autoresponded,
            response.response_time,
            response.p_proposal,
            response.r_decision,
        ]


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
        "iteround.total_score.P",
        "iteround.total_score.R",
        #
        "trial.iteration",
        "trial.status",
        "trial.completion",
        "trial.processing_time",
        "trial.endowment",
        "trial.proposal",
        "trial.decision",
        "trial.score.P",
        "trial.score.R",
    ]

    for trial in Trial.totall():
        iteround = trial.iteround
        group = iteround.group

        yield [
            group.session.code,
            group.session.label,
            None,
            None,
            group.condition,
            #
            iteround.pagename,
            iteround.status,
            iteround.completion,
            f"{iteround.processing_time:.01f}" if iteround.processing_time else None,
            iteround.progress_trials,
            iteround.total_score_p,
            iteround.total_score_r,
            #
            trial.iteration,
            trial.status,
            trial.completion,
            f"{trial.processing_time:.01f}" if trial.processing_time else None,
            trial.endowment,
            trial.proposal,
            trial.decision,
            trial.score_p,
            trial.score_r,
        ]
