from typing import NamedTuple

from _extras.tracking import track_players_all_around, track_players_all_atrial, track_round_trials
from units import Coins

from .conf import C
from .models import Player, Group, Round, Trial, Response
from .models import set_payoff
from .autoresponding import make_proposal, make_decision


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
    def stage(self) -> str | None:
        assert self.trial is not None
        return self.trial.progress_stage

    @property
    def turn(self) -> str | None:
        assert self.trial is not None
        return C.STAGEROLES[self.trial.progress_stage] if self.trial.is_running and self.trial.progress_stage else None

    @property
    def autoresponding(self) -> bool:
        assert self.iteround is not None and self.trial is not None and self.trial.is_running
        return self.iteround.autorespond_role == self.turn


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


def advance(current: Progress) -> Progress:
    """Advance current round one iteration further"""
    pagename, player, iteround, trial = current
    assert trial is None or trial.is_closed, "Invalid advancing over incomplete trial"

    iteround = advance_round(current, iteround)

    if not iteround.is_closed:
        trial = advance_trial(current, iteround, trial)

    return Progress(pagename, player, iteround, trial)


def advance_round(current: Progress, iteround: Round | None) -> Round:
    if iteround is None:
        iteround = Round.pick(current.pagename, group=current.group)

    if iteround.is_pristine and track_players_all_around(current.player, iteround):
        iteround.start()

    if iteround.is_running and not track_round_continue(iteround):
        iteround.complete()
        set_payoff(current.group, iteround)

    return iteround


def advance_trial(current: Progress, iteround: Round, trial: Trial | None) -> Trial:
    if trial is None:
        trial = Trial.pick_next(iteround)

    if trial.is_pristine and track_players_all_atrial(current.player, trial):
        trial.start()

    if trial.is_running and not track_trial_continue(trial):
        trial.complete()

    track_round_continue(iteround)

    return trial


def respond_proposal(current: Progress, proposal: Coins, **kwargs) -> Response:
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"

    assert player.role == current.turn
    response = Response.create_next(trial, player, stage=trial.progress_stage, p_proposal=proposal, **kwargs)

    advance_trial(current, iteround, trial)
    return response


def respond_decision(current: Progress, decision: str, **kwargs) -> Response:
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"

    assert player.role == current.turn
    response = Response.create_next(trial, player, stage=trial.progress_stage, r_decision=decision, **kwargs)

    advance_trial(current, iteround, trial)
    return response


async def autorespond_proposal(current: Progress) -> Response:
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"
    assert trial.progress_stage == "PROPOSING"

    response = Response.create_next(trial, player, stage=trial.progress_stage)
    await make_proposal(trial, response)

    advance_trial(current, iteround, trial)
    return response


async def autorespond_decision(current: Progress) -> Response:
    # TODO: seperate into 2 autorespond_ s
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"
    assert trial.progress_stage == "DECIDING"

    response = Response.create_next(trial, player, stage=trial.progress_stage)
    await make_decision(trial, response)

    advance_trial(current, iteround, trial)
    return response


def timeout(current: Progress):
    """Handle timeout, reported from a waiting (live) player"""
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"

    [other] = player.get_others_in_group()
    other.participant.status = "dropout"

    iteround.autorespond_role = other.role
    advance_trial(current, iteround, trial)
