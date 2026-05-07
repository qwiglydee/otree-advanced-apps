from typing import NamedTuple

from _stuff.participant import current_pagename

from .const import C  # noqa
from .models import Player, Round, Trial, Response


def max_trials(iteround: Round):
    return C.NUM_TRIALS[iteround.pagename]


def track_round(iteround: Round):
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')


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

    @property
    def is_valid(self):
        return self.iteround and self.trial

    @property
    def has_started(self):
        return self.trial and self.trial.has_started

    @property
    def is_running(self):
        return self.trial and self.trial.is_started

    @property
    def turn(self):
        return self.trial.progress_turn if self.trial else None


def current(player: Player):
    group = player.group
    pagename = current_pagename(player.participant)
    iteround = Round.current(pagename, group=group)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def advance(current: Progress) -> Progress:
    pagename, player, iteround, trial = current
    group = player.group

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
        return Progress(pagename, player, iteround, None)

    if trial is None:
        trial = Trial.advance_next(iteround)

    all_around = track_players_trial(player, trial)
    if trial.is_pristine and all_around:
        trial.start()
        trial.update()
        trial.progress_turn = C.TURNS[0]

    return Progress(pagename, player, iteround, trial)


def respond(current: Progress, **kwargs) -> Response:
    assert current.is_valid
    pagename, player, iteround, trial = current
    turn = current.turn

    assert player.role == turn
    response = Response.create_next(trial, player)
    response.respond(**kwargs)

    trial.update()

    if turn == C.TURNS[-1]:
        trial.complete()
        trial.progress_turn = None
    else:
        # next turn
        turn_idx = C.TURNS.index(turn)
        trial.progress_turn = C.TURNS[turn_idx + 1]

    iteround.update()
    track_round(iteround)

    return response
