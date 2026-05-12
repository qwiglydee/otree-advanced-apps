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
    def stage(self):
        return self.trial.progress_stage if self.is_running else None

    @property
    def retries_left(self):
        assert self.trial
        return C.NUM_RETRIES.get(self.pagename, 1) - self.trial.progress_retries


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
    trial.progress_retries = Response.count(trial, stage='ANSWER')
    trial.progress_stage = 'ANSWER' if trial.strategy else 'DECISION'
    return trial.progress_retries < C.NUM_RETRIES.get(trial.iteround.pagename, 1) and not trial.success


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


def respond_decision(curr: Progress, decision: str, **kwargs):
    assert curr.is_valid and curr.stage == 'DECISION'
    pagename, player, iteround, trial = curr

    response = Response.create_next(trial, player, stage='DECISION', decision=decision, **kwargs)
    track_trial(trial)

    advance_trial(curr)
    return response


def respond_answer(curr: Progress, answer: str, **kwargs) -> Response:
    assert curr.is_valid and curr.stage == 'ANSWER'
    pagename, player, iteround, trial = curr

    response = Response.create_next(trial, player, stage='ANSWER', answer=answer, **kwargs)
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
