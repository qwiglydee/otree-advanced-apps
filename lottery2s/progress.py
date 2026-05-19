from typing import NamedTuple

from _stuff.tracking import track_round_trials

from .conf import C  # noqa
from .models import Player, Round, Trial, Response
from .models import set_payoff


class Progress(NamedTuple):
    pagename: str
    player: Player
    iteround: Round | None
    trial: Trial | None

    @property
    def is_running(self) -> bool:
        return self.trial is not None and self.trial.is_running

    @property
    def is_finalizable(self):
        assert self.trial is not None and self.trial.is_running
        return self.trial.progress_samples >= C.MIN_SAMPLES


def current(page, player: Player) -> Progress:
    """Get current round and trial (maybe none yet)"""
    pagename = page.__name__
    iteround = Round.current(pagename, player=player)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def track_round_continue(iteround: Round) -> bool:
    """Track round progress state and decide if to continue"""
    iteround.update()
    return track_round_trials(iteround, Trial, C.NUM_TRIALS[iteround.pagename])


def track_trial_continue(trial: Trial) -> bool:
    """Track trial progress state and decide if to continue"""
    trial.update()
    trial.progress_samples = Response.count(trial, stage="SAMPLING")
    return Response.count(trial, stage="FINAL") == 0


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
        iteround = Round.pick(curr.pagename, player=curr.player)

    if iteround.is_pristine:
        iteround.start()

    if iteround.is_running and not track_round_continue(iteround):
        iteround.complete()
        set_payoff(curr.player, iteround)

    return iteround


def advance_trial(curr: Progress, iteround: Round, trial: Trial | None) -> Trial:
    if trial is None:
        trial = Trial.pick_next(iteround)

    if trial.is_pristine:
        trial.start()

    if trial.is_running and not track_trial_continue(trial):
        trial.complete()

    track_round_continue(iteround)

    return trial


def respond(curr: Progress, stage: str, choice: str, **kwargs) -> Response:
    pagename, player, iteround, trial = curr
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"

    if stage == "FINAL":
        assert curr.is_finalizable

    response = Response.create_next(trial, player, stage=stage, choice=choice, **kwargs)
    response.evaluate()

    advance_trial(curr, iteround, trial)
    return response
