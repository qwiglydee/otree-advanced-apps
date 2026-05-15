from otree import database
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Session, Participant
from otree.forms import widgets

from _stuff.itermodels import BaseRoundModel, BaseTrialModel, BaseResponseModel
from _stuff.dictprop import dictprop

from .conf import C, config_condition, Points


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    condition = database.StringField()

    @property
    def endowment(self):
        return C.ENDOWMENT[self.condition]


class Player(BasePlayer):
    age = database.IntegerField()
    gender = database.StringField(
        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
        widget=widgets.RadioSelect
    )

    total_score = database.DecimalField(unit=Points, initial=0)

    progress_round = database.IntegerField()
    progress_trial = database.IntegerField()

    def get_partner(self):
        if self.role == 'P':
            return self.group.get_player_by_role('R')
        if self.role == 'R':
            return self.group.get_player_by_role('P')


class Round(BaseRoundModel):
    group: Group = database.Link(Group)

    total_score_p = database.DecimalField(unit=Points, initial=0)
    total_score_r = database.DecimalField(unit=Points, initial=0)
    total_scores = dictprop("total_score_", ('P', 'R'))

    def init(self, **kwargs):
        pass

    def update(self):
        pass

    progress_trials = database.IntegerField()


class Trial(BaseTrialModel):
    iteround: Round = database.Link(Round)

    endowment = database.DecimalField(unit=Points)
    proposal = database.DecimalField(unit=Points)
    decision = database.StringField(choices=C.DECISIONS)

    score_p = database.DecimalField(unit=Points, initial=0)
    score_r = database.DecimalField(unit=Points, initial=0)
    scores = dictprop("score_", ('P', 'R'))

    @property
    def outcomes(self):
        return {C.P_ROLE: self.score_p, C.R_ROLE: self.score_r}

    @property
    def condition(self) -> str:
        return self.iteround.group.condition

    def init(self, **kwargs):
        self.endowment = C.ENDOWMENT[self.condition]

    def update(self):
        proposed = Response.last(self, stage='PROPOSING')
        self.proposal = proposed.p_proposal if proposed else None
        decided = Response.last(self, stage='DECIDING')
        self.decision = decided.r_decision if decided else None

    def complete(self):
        self.close('COMPLETED')
        if self.decision == 'ACCEPT':
            self.score_p = self.endowment - self.proposal
            self.score_r = self.proposal
            self.iteround.total_score_p += self.score_p
            self.iteround.total_score_r += self.score_r

    progress_stage = database.StringField()


class Response(BaseResponseModel):
    trial: Trial = database.Link(Trial)
    stage = database.StringField()
    player: Player = database.Link(Player)

    response_time = database.IntegerField()
    p_proposal = database.DecimalField(unit=Points)
    r_decision = database.StringField(choices=C.DECISIONS)


def setup_group(group: Group):
    group.condition = config_condition(group.session)


def set_payoffs(group: Group, iteround: Round):
    scores = iteround.total_scores
    for player in group.get_players():
        player.total_score = scores[player.role]
        if player.participant.status != 'dropout':
            player.payoff = player.total_score


def custom_export_responses(_):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
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

    for response in Response.objects_filter().order_by('trial_id', 'iteration'):
        trial: Trial = response.trial
        iteround: Round = trial.iteround
        player: Player = response.player
        session: Session = player.session
        participant: Participant = player.participant

        yield [
            session.code,
            session.label,
            participant.code,
            participant.label,
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
            response.r_decision
        ]


def custom_export_trials(_):
    yield [
        "session.code",
        "session.label",
        "participant.code",
        "participant.label",
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

    for trial in Trial.objects_filter().order_by('iteround_id', 'iteration'):
        iteround: Round = trial.iteround
        group: Group = iteround.group
        session: Session = group.session

        yield [
            session.code,
            session.label,
            None,
            None,
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
