from typing import NamedTuple

from _stuff.participant import current_pagename

from .const import C  # noqa
from .models import Player, Round, Trial, Response


class Progress(NamedTuple):
    pagename: str
    player: Player
    iteround: Round | None
    trial: Trial | None
    response: Response | None

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
    return Progress(pagename, player, iteround, trial, None)


def advance(current: Progress) -> Progress:
    pagename, player, iteround, trial, response = current
    assert response is None

    if iteround is None:
        iteround = Round.advance(pagename, player=player)
        trial = None

    if iteround.is_pristine:
        iteround.start()

    advancing = advancing_round(iteround)

    if not advancing:
        iteround.complete()

    if iteround.is_closed:
        return Progress(pagename, player, iteround, None, None)

    if trial is None:
        trial = Trial.advance_next(iteround)

    if trial.is_pristine:
        trial.start()

    return Progress(pagename, player, iteround, trial, None)


def respond(current: Progress, response_time: int, answer: str) -> Progress:
    pagename, player, iteround, trial, response = current
    assert current.is_valid and response is None

    response = Response.respond(trial, player, response_time, answer)
    advancing = advancing_trial(trial)

    if not advancing:
        trial.complete()

    advancing_round(iteround)

    return Progress(pagename, player, iteround, trial, response)


def advancing_round(iteround: Round):
    iteround.update()
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')
    return iteround.progress_trials < max_trials(iteround)


def max_trials(iteround: Round):
    return C.NUM_TRIALS[iteround.pagename]


def advancing_trial(trial: Trial):
    trial.update()
    return False
