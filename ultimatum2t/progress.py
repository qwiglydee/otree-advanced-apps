from typing import NamedTuple

from _stuff.tracking import track_players_all_around, track_players_all_atrial, track_round_trials
from units import Points

from .conf import C
from .models import Player, Group, Round, Trial, Response
from .models import set_payoff


class Progress(NamedTuple):
    pagename: str
    player: Player
    iteround: Round | None
    trial: Trial | None

    @property
    def group(self) -> Group:
        return self.player.group  # type: ignore

    @property
    def is_running(self) -> bool:
        return self.trial is not None and self.trial.is_running

    @property
    def stage(self) -> str:
        assert self.trial is not None and self.trial.is_running
        return self.trial.progress_stage

    @property
    def turn(self) -> str:
        assert self.trial is not None and self.trial.is_running
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
        trial.progress_stage = ""
    return trial.progress_stage != ""


def advance(curr: Progress) -> Progress:
    """Advance current round one iteration further"""
    pagename, player, iteround, trial = curr
    assert trial is None or trial.is_closed, "Invalid advancing over incomplete trial"

    iteround = advance_round(curr, iteround)

    if not iteround.is_closed:
        trial = advance_trial(curr, iteround, trial)

    return Progress(pagename, player, iteround, trial)


def advance_round(curr: Progress, iteround: Round | None) -> Round:

    if iteround is None:
        iteround = Round.pick(curr.pagename, group=curr.group)

    if iteround.is_pristine and track_players_all_around(curr.player, iteround):
        iteround.start()

    if iteround.is_running and not track_round_continue(iteround):
        iteround.complete()
        set_payoff(curr.group, iteround)

    return iteround


def advance_trial(curr: Progress, iteround: Round, trial: Trial | None) -> Trial:
    if trial is None:
        trial = Trial.pick_next(iteround)

    if trial.is_pristine and track_players_all_atrial(curr.player, trial):
        trial.start()

    if trial.is_running and not track_trial_continue(trial):
        trial.complete()

    track_round_continue(iteround)

    return trial


def respond_proposal(curr: Progress, proposal: Points, **kwargs) -> Response:
    pagename, player, iteround, trial = curr
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"

    assert player.role == curr.turn
    response = Response.create_next(trial, player, stage=trial.progress_stage, p_proposal=proposal, **kwargs)

    advance_trial(curr, iteround, trial)
    return response


def respond_decision(curr: Progress, decision: str, **kwargs) -> Response:
    pagename, player, iteround, trial = curr
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"

    assert player.role == curr.turn
    response = Response.create_next(trial, player, stage=trial.progress_stage, r_decision=decision, **kwargs)

    advance_trial(curr, iteround, trial)
    return response


def timeout(curr: Progress):
    """Handle timeout, reported from a waiting (live) player"""
    pagename, player, iteround, trial = curr
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"

    other = player.group.get_player_by_role(C.PARTNEROLES[player.role])
    other.participant.status = "dropout"

    trial.close("TIMEOUT")
    iteround.close("TIMEOUT")
    set_payoff(iteround.group, iteround)
