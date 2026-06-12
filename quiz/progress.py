from typing import NamedTuple

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


def current(page, player: Player) -> Progress:
    pagename = page.__name__
    iteround = Round.current(pagename, player=player)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def track_round_progress(iteround: Round) -> bool:
    iteround.progress_trials = Trial.count(iteround, status="CLOSED")
    return iteround.progress_trials < C.NUM_TRIALS[iteround.pagename]


def track_trial_progress(trial: Trial) -> bool:
    return Response.count(trial) < 1


def advance(current: Progress) -> Progress:
    pagename, player, iteround, trial = current
    assert trial is None or trial.is_closed, "Invalid advancing over incomplete trial"

    iteround = advance_round(current, iteround)

    if not iteround.is_closed:
        trial = advance_trial(current, iteround, trial)

    return Progress(pagename, player, iteround, trial)


def advance_round(current: Progress, iteround: Round | None) -> Round:
    if iteround is None:
        iteround = Round.pick(current.pagename, player=current.player)

    if iteround.is_pristine:
        iteround.start()

    iteround.update()

    if iteround.is_running and not track_round_progress(iteround):
        iteround.complete()
        set_payoff(current.player, iteround)

    return iteround


def advance_trial(current: Progress, iteround: Round, trial: Trial | None) -> Trial:
    if trial is None:
        trial = Trial.pick_next(iteround)

    if trial.is_pristine:
        trial.start()

    trial.update()

    if trial.is_running and not track_trial_progress(trial):
        trial.complete()

    track_round_progress(iteround)

    return trial


def respond(current: Progress, answer: str, **kwargs) -> Response:
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"

    response = Response.create_next(trial, player, answer=answer, **kwargs)
    response.evaluate()

    advance_trial(current, iteround, trial)
    return response
