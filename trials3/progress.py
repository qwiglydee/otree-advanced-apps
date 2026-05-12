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
        return max_retries(self.trial) - self.trial.progress_retries


def max_trials(iteround: Round):
    return C.NUM_TRIALS[iteround.pagename]


def max_retries(trial):
    return C.NUM_RETRIES.get(trial.iteround.pagename, 1)


def track_round(iteround: Round):
    iteround.update()
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')


def track_trial(trial: Trial):
    trial.update()
    trial.progress_retries = Response.count(trial, stage='ANSWER')
    trial.progress_stage = 'ANSWER' if trial.strategy else 'DECISION'


def current(player: Player) -> Progress:
    pagename = current_pagename(player.participant)
    iteround = Round.current(pagename, player=player)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def advance(current: Progress) -> Progress:
    pagename, player, iteround, trial = current

    if iteround is None:
        iteround = Round.advance(pagename, player=player)
        trial = None

    if iteround.is_pristine:
        iteround.start()

    track_round(iteround)

    if iteround.progress_trials >= max_trials(iteround):
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


def respond_decision(current: Progress, decision: str, **kwargs):
    assert current.is_valid and current.stage == 'DECISION'
    pagename, player, iteround, trial = current

    response = Response.create_next(trial, player, stage='DECISION', decision=decision, **kwargs)
    track_trial(trial)

    return response


def respond_answer(current: Progress, answer: str, **kwargs) -> Response:
    assert current.is_valid and current.stage == 'ANSWER'
    pagename, player, iteround, trial = current

    response = Response.create_next(trial, player, stage='ANSWER', answer=answer, **kwargs)
    response.evaluate()
    track_trial(trial)

    if trial.success or trial.progress_retries >= max_retries(trial):
        trial.complete()
        track_round(iteround)

    return response
