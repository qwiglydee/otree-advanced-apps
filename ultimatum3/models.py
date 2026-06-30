from decimal import Decimal

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models

from _extras.keyprop import dict_getter, key_getter
from _extras.itermodels import BaseResponseModel, BaseRoundModel, BaseTrialModel
from _extras.screening import copy_fields, post_assign_role
from _extras.score import score_to_currency

from units import Coins

from .conf import C


class Subsession(BaseSubsession):
    condition = models.StringField()
    quelen_p = models.IntegerField(initial=0)
    quelen_r = models.IntegerField(initial=0)
    quelen = models.IntegerField(initial=0)


class Group(BaseGroup):
    @property
    def condition(self):
        return self.subsession.condition  # type: ignore

    @property
    def endowment(self):
        return C.ENDOWMENT[self.condition]


def setup_group(group: Group):
    for player in group.get_players():
        post_assign_role(player)
        setup_player(player)


class Player(BasePlayer):
    age = models.IntegerField()
    gender = models.StringField()

    total_score = models.DecimalField(unit=Coins, initial=0)

    progress_round = models.IntegerField()
    progress_trial = models.IntegerField()

    @property
    def condition(self):
        return self.subsession.condition  # type: ignore


def setup_player(player: Player):
    from ultimatum3_screener import Player as ScrPlayer

    scrplayer = ScrPlayer.get_matching(player)
    copy_fields(scrplayer, player, C.SCREENERFIELDS)


class Round(BaseRoundModel):
    group: Group = models.Link(Group)

    total_score_p = models.DecimalField(unit=Coins, initial=0)
    total_score_r = models.DecimalField(unit=Coins, initial=0)
    get_score = key_getter("total_score_")

    def init(self):
        pass

    def update(self):
        pass

    progress_trials = models.IntegerField(initial=0)


class Trial(BaseTrialModel):
    iteround: Round = models.Link(Round)

    endowment = models.DecimalField(unit=Coins)
    proposal = models.DecimalField(unit=Coins)
    response = models.StringField()

    score_p = models.DecimalField(unit=Coins)
    score_r = models.DecimalField(unit=Coins)
    get_scores = dict_getter("score_", ("P", "R"))

    def init(self):
        self.endowment = C.ENDOWMENT[self.iteround.group.condition]

    def update(self):
        proposed = Response.last(self, stage="PROPOSING")
        if proposed:
            self.proposal = proposed.proposal
        responded = Response.last(self, stage="RESPONDING")
        if responded:
            self.response = responded.decision

    def complete(self):
        assert self.proposal is not None and self.response is not None
        self.close("COMPLETED")
        scores = evaluate(self.endowment, self.proposal, self.response == "ACCEPT")
        self.score_p = scores["P"]
        self.score_r = scores["R"]
        self.iteround.total_score_p += self.score_p
        self.iteround.total_score_r += self.score_r

    progress_responses = models.IntegerField(initial=0)


def evaluate(endowment: Decimal, proposed: Decimal, accepted: bool) -> dict[str, Decimal]:
    """The main game rule"""
    # using Decimals because otree fields are broken-typed
    if accepted:
        return {"R": proposed, "P": Decimal(endowment - proposed)}
    else:
        return {"R": Decimal(0), "P": Decimal(0)}


class Response(BaseResponseModel):
    trial: Trial = models.Link(Trial)
    player: Player = models.Link(Player)
    response_time = models.IntegerField()

    stage = models.StringField()
    proposal = models.DecimalField(unit=Coins)
    decision = models.StringField()


def set_payoff(iteround: Round):
    group = iteround.group
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
        "trial.response",
        "trial.score.P",
        "trial.score.R",
        #
        "response.iteration",
        "response.stage",
        "player.role",
        "response.response_time",
        "response.proposal",
        "response.response",
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
            trial.response,
            trial.score_p,
            trial.score_r,
            #
            response.iteration,
            response.stage,
            player.role,
            response.response_time,
            response.proposal,
            response.decision,
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
        "trial.response",
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
            trial.response,
            trial.score_p,
            trial.score_r,
        ]
