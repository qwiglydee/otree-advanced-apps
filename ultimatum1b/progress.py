from typing import NamedTuple


from .conf import C, Points
from .models import Player, Round, Trial, Response
from .models import set_payoffs


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
    def stage(self):
        return self.trial.progress_stage if self.trial else None

    @property
    def turn(self) -> int:
        return C.STAGEROLES[self.trial.progress_stage] if self.is_running else None


def current(page, player: Player) -> Progress:
    """Get current round and trial (maybe none yet)"""
    pagename = page.__name__
    iteround = Round.current(pagename, player=player)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def track_round_running(iteround: Round) -> bool:
    """Track round progress state and decide if to continue"""
    iteround.update()
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')
    return iteround.progress_trials < C.NUM_TRIALS


def track_trial_running(trial: Trial) -> bool:
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

    iteround = advance_round(pagename, player, iteround)

    if not iteround.is_closed:
        trial = advance_trial(player, iteround, trial)

    return Progress(pagename, player, iteround, trial)


def advance_round(pagename: str, player: Player, iteround: Round) -> Round:
    if iteround is None:
        iteround = Round.advance(pagename, player=player)

    if iteround.is_pristine:
        iteround.start()

    if iteround.is_running and not track_round_running(iteround):
        iteround.complete()
        set_payoffs(player, iteround)

    return iteround


def advance_trial(player: Player, iteround: Round, trial: Trial) -> Progress:
    if trial is None:
        trial = Trial.advance_next(iteround)

    if trial.is_pristine:
        trial.start()

    if trial.is_running and track_trial_running(trial):
        autorespond(player, iteround, trial)

    if trial.is_running and not track_trial_running(trial):
        trial.complete()
        track_round_running(iteround)

    return trial


def respond_proposal(curr: Progress, proposal: Points, **kwargs) -> Response:
    assert curr.is_valid
    pagename, player, iteround, trial = curr

    assert player.role == curr.turn
    response = Response.create_next(trial, player, stage=trial.progress_stage, p_proposal=proposal, **kwargs)

    advance_trial(player, iteround, trial)
    return response


def respond_decision(curr: Progress, decision: str, **kwargs) -> Response:
    assert curr.is_valid
    pagename, player, iteround, trial = curr

    assert player.role == curr.turn
    response = Response.create_next(trial, player, stage=trial.progress_stage, r_decision=decision, **kwargs)

    advance_trial(player, iteround, trial)
    return response


def autorespond(player: Player, iteround: Round, trial: Trial):
    curr_turn = C.STAGEROLES[trial.progress_stage] if trial.progress_stage else None
    print("autoresponding:", trial, curr_turn == iteround.autoresponding)
    if curr_turn == iteround.autoresponding:
        response = Response.create_next(trial, player, stage=trial.progress_stage)
        response.autorespond()
        return response
