from decimal import Decimal

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models, widgets

from _extras.keyprop import dict_getter, key_getter
from _extras.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from _extras.score import score_to_currency

from units import Coins

from .conf import C, config_condition


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    condition = models.StringField()


class Player(BasePlayer):
    age = models.IntegerField()
    gender = models.StringField(choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], widget=widgets.RadioSelect)

    total_score = models.DecimalField(unit=Coins, initial=0)

    progress_round = models.IntegerField()
    progress_trial = models.IntegerField()

    @property
    def condition(self):
        return self.group.condition  # type: ignore


class Round(BaseRoundModel):
    group: Group = models.Link(Group)

    total_score_p = models.DecimalField(unit=Coins, initial=0)
    total_score_r = models.DecimalField(unit=Coins, initial=0)
    get_score = key_getter("total_score_")

    def init(self):
        pass

    def update(self):
        pass

    progress_trials = models.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = models.Link(Round)

    endowment = models.DecimalField(unit=Coins)
    proposal = models.DecimalField(unit=Coins)
    decision = models.StringField(choices=C.DECISIONS)

    score_p = models.DecimalField(unit=Coins)
    score_r = models.DecimalField(unit=Coins)
    get_scores = dict_getter("score_", ("P", "R"))

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

    response_time = models.IntegerField()
    p_proposal = models.DecimalField(unit=Coins)
    r_decision = models.StringField(choices=C.DECISIONS)


def setup_group(group: Group):
    group.condition = config_condition(group.session)


def set_payoff(group: Group, iteround: Round):
    for player in group.get_players():
        player.total_score = iteround.get_score(player.role)
        if player.participant.status != "dropout":
            player.payoff = score_to_currency(player.total_score, player.session)  # type: ignore currency incompatibility


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
