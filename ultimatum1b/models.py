from decimal import Decimal

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models

from _stuff.keyprop import dict_getter, key_getter

from _stuff.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from units import Coins

from .conf import C


def PointsField(**kwargs):
    return models.DecimalField(unit=Coins, **kwargs)  # type: ignore internal incompatibility


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()

    total_score = PointsField(initial=0)


class Round(BaseRoundModel):
    player: Player = models.Link(Player)

    total_score_p = PointsField(initial=0)
    total_score_r = PointsField(initial=0)
    get_score = key_getter("total_score_")

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
    get_scores = dict_getter("score_", ("P", "R"))

    @property
    def condition(self) -> str:
        return self.iteround.player.condition

    def init(self):
        self.endowment = C.ENDOWMENT[self.condition]

    def update(self):
        proposed = Response.last(self, stage="PROPOSING")
        self.proposal = proposed.p_proposal if proposed else None
        decided = Response.last(self, stage="DECIDING")
        self.decision = decided.r_decision if decided else None

    def complete(self):
        assert self.proposal is not None and self.decision is not None
        self.close("COMPLETED")
        scores = evaluate(self.endowment, self.proposal, self.decision == "ACCEPT")
        self.score_p = scores["P"]
        self.score_r = scores["R"]
        self.iteround.total_score_p += self.score_p
        self.iteround.total_score_r += self.score_r

    progress_stage = models.StringField()


def evaluate(endowment: Decimal, proposed: Decimal, accepted: bool) -> dict[str, Decimal]:
    """The main game rule"""
    # using Decimals because otree fields are broken-typed
    if accepted:
        return {"R": proposed, "P": Decimal(endowment - proposed)}
    else:
        return {"R": Decimal(0), "P": Decimal(0)}


class Response(BaseResponseModel):
    trial: Trial = models.Link(Trial)
    stage = models.StringField()
    player: Player = models.Link(Player)
    autoresponded = models.BooleanField(initial=False)

    response_time = models.IntegerField()
    p_proposal = PointsField()
    r_decision = models.StringField(choices=C.DECISIONS)


def set_payoff(player: Player, iteround: Round):
    player.total_score = iteround.get_score(player.role)
    if player.participant.status != "dropout":
        player.payoff = player.total_score.to_real_world_currency(player.session)  # type: ignore


def custom_export_responses(_):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
        "condition",
        "player.role",
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
        player = response.player

        yield [
            player.session.code,
            player.session.label,
            player.participant.code,
            player.participant.label,
            player.condition,
            player.role,
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
        "player.role",
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
        player = iteround.player

        yield [
            player.session.code,
            player.session.label,
            player.participant.code,
            player.participant.label,
            player.condition,
            player.role,
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
