from typing import NamedTuple

from _stuff.participant import current_pagename

from .const import C  # noqa
from .models import Player, Round, Trial, Response


def max_trials(iteround: Round):
    return C.NUM_TRIALS[iteround.pagename]


def track_round(iteround: Round):
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')


def max_retries(trial: Trial):
    return C.NUM_RETRIES.get(trial.iteround.pagename, 1)


def track_trial(trial: Trial):
    trial.progress_retries = Response.count(trial)


class Progress(NamedTuple):
    pagename: str
    player: Player
    iteround: Round | None
    trial: Trial | None

    @property
    def is_valid(self):
        return self.iteround and self.trial

    @property
    def has_started(self):
        return self.trial and self.trial.has_started

    @property
    def is_running(self):
        return self.trial and self.trial.is_started


def current(player: Player):
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

    iteround.update()
    track_round(iteround)

    if iteround.progress_trials >= max_trials(iteround):
        iteround.complete()

    if iteround.is_closed:
        return Progress(pagename, player, iteround, None)

    if trial is None:
        trial = Trial.advance_next(iteround)

    if trial.is_pristine:
        trial.start()
        trial.update()
        track_trial(trial)

    return Progress(pagename, player, iteround, trial)


def respond(current: Progress, **kwargs) -> Response:
    assert current.is_valid
    pagename, player, iteround, trial = current

    response = Response.create_next(trial, player)
    response.respond(**kwargs)

    trial.update()
    track_trial(trial)

    if trial.progress_retries >= max_retries(trial) or trial.success:
        trial.complete()

    iteround.update()
    track_round(iteround)

    return response
