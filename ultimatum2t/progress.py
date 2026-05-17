from typing import NamedTuple

from _stuff.tracking import track_players_all_around, track_players_all_atrial, track_round_trials

from .conf import C, Points
from .models import Player, Group, Round, Trial, Response
from .models import set_payoff


class Progress(NamedTuple):
    pagename: str
    player: Player
    iteround: Round | None
    trial: Trial | None

    @property
    def is_valid(self) -> bool:
        return self.iteround and self.trial

    @property
    def is_running(self) -> bool:
        return self.trial and self.trial.is_running

    @property
    def stage(self) -> str:
        assert self.is_running
        return self.trial.progress_stage

    @property
    def turn(self) -> str:
        assert self.is_running
        return C.STAGEROLES[self.trial.progress_stage]


def current(page, player: Player) -> Progress:
    """Get current round and trial (maybe none yet)"""
    pagename = page.__name__
    iteround = Round.current(pagename, group=player.group)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def track_round_continue(iteround: Round) -> bool:
    """Track round progress state and decide if to continue"""
    iteround.update()
    return track_round_trials(iteround, Trial, C.NUM_TRIALS)


def track_trial_continue(trial: Trial) -> bool:
    """Track trial progress state and decide if to continue"""
    trial.update()
    if trial.proposal is None:
        trial.progress_stage = "PROPOSING"
    elif trial.decision is None:
        trial.progress_stage = "DECIDING"
    else:
        trial.progress_stage = None
    return trial.progress_stage is not None


def advance(curr: Progress) -> Progress:
    """Advance current round one iteration further"""
    pagename, player, iteround, trial = curr
    assert trial is None or trial.is_closed, "Invalid advancing over incomplete trial"

    iteround = advance_round(player, pagename, iteround)

    if not iteround.is_closed:
        trial = advance_trial(player, iteround, trial)

    return Progress(pagename, player, iteround, trial)


def advance_round(player: Player, pagename: str, iteround: Round | None) -> Round:
    group: Group = player.group

    if iteround is None:
        iteround = Round.advance(pagename, group=group)

    if iteround.is_pristine and track_players_all_around(player, iteround):
        iteround.start()

    if iteround.is_running and not track_round_continue(iteround):
        iteround.complete()
        set_payoff(group, iteround)

    return iteround


def advance_trial(player: Player, iteround: Round, trial: Trial | None) -> Trial:
    if trial is None:
        trial = Trial.advance_next(iteround)

    if trial.is_pristine and track_players_all_atrial(player, trial):
        trial.start()

    if trial.is_running and not track_trial_continue(trial):
        trial.complete()

    track_round_continue(iteround)

    return trial


def respond_proposal(curr: Progress, proposal: Points, **kwargs) -> Response:
    assert curr.is_running
    pagename, player, iteround, trial = curr

    assert player.role == curr.turn
    response = Response.create_next(trial, player, stage=trial.progress_stage, p_proposal=proposal, **kwargs)

    advance_trial(player, iteround, trial)
    return response


def respond_decision(curr: Progress, decision: str, **kwargs) -> Response:
    assert curr.is_running
    pagename, player, iteround, trial = curr

    assert player.role == curr.turn
    response = Response.create_next(trial, player, stage=trial.progress_stage, r_decision=decision, **kwargs)

    advance_trial(player, iteround, trial)
    return response


def timeout(curr: Progress):
    """Handle timeout, reported from a waiting (live) player"""
    assert curr.is_running
    pagename, player, iteround, trial = curr

    other = player.group.get_player_by_role(C.PARTNEROLES[player.role])
    other.participant.status = 'dropout'

    trial.close('TIMEOUT')
    iteround.close('TIMEOUT')
    set_payoff(iteround.group, iteround)
