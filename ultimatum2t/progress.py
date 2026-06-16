from typing import NamedTuple

from _extras.tracking import all_players_around, all_players_atrial
from units import Coins

from .conf import C
from .models import Group, Player, Response, Round, Trial, set_payoff


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
        return self.trial.progress_stage if self.trial is not None else None


def current(page, player: Player) -> Progress:
    pagename = page.__name__
    iteround = Round.current(pagename, group=player.group)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def track_round_progress(iteround: Round) -> bool:
    iteround.progress_trials = Trial.count(iteround, status="CLOSED")
    return iteround.progress_trials < C.NUM_TRIALS


def track_trial_progress(trial: Trial) -> bool:
    proposed = Response.count(trial, stage="PROPOSING")
    decided = Response.count(trial, stage="DECIDING")
    if not proposed:
        trial.progress_stage = "PROPOSING"
    elif not decided:
        trial.progress_stage = "DECIDING"
    else:
        trial.progress_stage = ""
    return trial.progress_stage != ""


def advance(current: Progress) -> Progress:
    pagename, player, iteround, trial = current
    assert trial is None or trial.is_closed, "Invalid advancing over incomplete trial"

    iteround = advance_round(current, iteround)

    if not iteround.is_closed:
        trial = advance_trial(current, iteround, trial)

    return Progress(pagename, player, iteround, trial)


def advance_round(current: Progress, iteround: Round | None) -> Round:
    if iteround is None:
        iteround = Round.pick(current.pagename, group=current.group)

    if iteround.is_pristine and all_players_around(current.player, iteround):
        iteround.start()

    iteround.update()

    if iteround.is_running and not track_round_progress(iteround):
        iteround.complete()
        set_payoff(current.group, iteround)

    return iteround


def advance_trial(current: Progress, iteround: Round, trial: Trial | None) -> Trial:
    if trial is None:
        trial = Trial.pick_next(iteround)

    if trial.is_pristine and all_players_atrial(current.player, trial):
        trial.start()

    trial.update()

    if trial.is_running and not track_trial_progress(trial):
        trial.complete()

    track_round_progress(iteround)

    return trial


def respond_proposal(current: Progress, proposal: Coins, **kwargs) -> Response:
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"
    assert current.stage == "PROPOSING" and player.role == "P"

    response = Response.create_next(trial, player, stage=trial.progress_stage, p_proposal=proposal, **kwargs)

    advance_trial(current, iteround, trial)
    return response


def respond_decision(current: Progress, decision: str, **kwargs) -> Response:
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"
    assert current.stage == "DECIDING" and player.role == "R"

    response = Response.create_next(trial, player, stage=trial.progress_stage, r_decision=decision, **kwargs)

    advance_trial(current, iteround, trial)
    return response


def timeout(current: Progress):
    """Handle timeout, reported from a waiting (live) player"""
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"

    [other] = player.get_others_in_group()
    other.participant.status = "dropout"

    trial.close("TIMEOUT")
    iteround.close("TIMEOUT")
    set_payoff(iteround.group, iteround)
