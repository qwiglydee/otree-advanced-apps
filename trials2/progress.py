from typing import NamedTuple

from _stuff.participant import current_pagename

from .const import C  # noqa
from .models import Player, Round, Trial, Response


def max_trials(iteround: Round):
    return C.NUM_TRIALS[iteround.pagename]


def track_round(iteround: Round):
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')


def track_trial(trial: Trial):
    count = Response.count(trial)
    trial.progress_stage = C.STAGES[count]


def track_players_round(player: Player, iteround: Round) -> bool:
    player.progress_round = iteround.id
    players = player.group.get_players()
    return all(p.field_maybe_none('progress_round') == iteround.id for p in players)


def track_players_trial(player: Player, trial: Trial) -> bool:
    player.progress_trial = trial.id
    players = player.group.get_players()
    return all(p.field_maybe_none('progress_trial') == trial.id for p in players)


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
    group = player.group
    pagename = current_pagename(player.participant)
    iteround = Round.current(pagename, group=group)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial, None)


def advance(current: Progress) -> Progress:
    pagename, player, iteround, trial, response = current
    group = player.group
    assert response is None

    if iteround is None:
        iteround = Round.advance(pagename, group=group)
        trial = None

    all_around = track_players_round(player, iteround)
    if iteround.is_pristine and all_around:
        iteround.start()

    iteround.update()
    track_round(iteround)

    if iteround.progress_trials >= max_trials(iteround):
        iteround.complete()

    if iteround.is_closed:
        return Progress(pagename, player, iteround, None, None)

    if trial is None:
        trial = Trial.advance_next(iteround)

    all_around = track_players_trial(player, trial)
    if trial.is_pristine and all_around:
        trial.start()

    if trial.is_started:
        trial.update()
        track_trial(trial)

    return Progress(pagename, player, iteround, trial, None)


def respond(current: Progress, **kwargs) -> Progress:
    pagename, player, iteround, trial, response = current
    assert current.is_valid and response is None
    assert current.player.role == C.ROLESMAP[current.trial.progress_stage]

    response = Response.create_next(trial, player, stage=trial.progress_stage)
    response.respond(**kwargs)

    trial.update()
    track_trial(trial)

    if trial.progress_stage == "COMPLETE":
        trial.complete()

    iteround.update()
    track_round(iteround)

    return Progress(pagename, player, iteround, trial, response)
