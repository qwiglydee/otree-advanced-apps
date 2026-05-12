from typing import NamedTuple

from _stuff.participant import current_pagename

from .conf import C  # noqa
from .models import Player, Round, Trial, Response
from .models import set_payoff


class Progress(NamedTuple):
    pagename: str
    player: Player
    iteround: Round | None
    trial: Trial | None

    @property
    def is_valid(self):
        return self.iteround and self.trial

    @property
    def is_running(self):
        return self.trial and self.trial.is_running

    @property
    def is_finalizable(self):
        return self.trial.progress_samples >= C.MIN_SAMPLES if self.trial else None


def current(player: Player) -> Progress:
    """Get current round and trial (maybe none yet)"""
    pagename = current_pagename(player.participant)
    iteround = Round.current(pagename, player=player)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def track_round(iteround: Round) -> bool:
    """Track round progress state and decide if to continue"""
    iteround.update()
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')
    return iteround.progress_trials < C.NUM_TRIALS[iteround.pagename]


def track_trial(trial: Trial) -> bool:
    """Track trial progress state and decide if to continue"""
    trial.update()
    trial.progress_samples = Response.count(trial, stage='SAMPLING')
    return Response.count(trial, stage='FINAL') == 0


def advance(curr: Progress) -> Progress:
    """Advance current round
    create/start/track round/trial
    """
    pagename, player, iteround, trial = curr

    if iteround is None:
        iteround = Round.advance(pagename, player=player)
        trial = None

    if iteround.is_pristine:
        iteround.start()

    if not track_round(iteround):
        iteround.complete()
        set_payoff(player, iteround)

    if iteround.is_closed:
        return Progress(pagename, player, iteround, None)

    if trial is None:
        trial = Trial.advance_next(iteround)

    if trial.is_pristine:
        trial.start()
        track_trial(trial)

    return Progress(pagename, player, iteround, trial)


def respond(curr: Progress, stage: str, choice: str, **kwargs) -> Response:
    assert curr.is_valid
    pagename, player, iteround, trial = curr

    if stage == 'FINAL':
        assert curr.is_finalizable

    response = Response.create_next(trial, player, stage=stage, choice=choice, **kwargs)
    response.evaluate()

    advance_trial(curr)
    return response


def advance_trial(curr: Progress):
    """Advance current trial
    Check completeness criteria, complete if needed
    """
    assert curr.is_valid
    pagename, player, iteround, trial = curr

    if not track_trial(trial):
        trial.complete()
        track_round(iteround)
