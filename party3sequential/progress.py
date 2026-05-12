from typing import NamedTuple

from _stuff.participant import current_pagename

from .conf import C  # noqa
from .models import Player, Group, Round, Trial, Response
from .models import set_payoffs


class Progress(NamedTuple):
    pagename: str
    player: Player
    iteround: Round | None
    trial: Trial | None

    @property
    def group(self) -> Group:
        return self.iteround.group

    @property
    def is_valid(self) -> bool:
        return self.iteround and self.trial

    @property
    def is_running(self) -> bool:
        return self.trial and self.trial.is_running

    @property
    def turn(self) -> int:
        return C.SEQUENCE[self.trial.progress_turn - 1] if self.is_running else None


def track_round(iteround: Round):
    iteround.update()
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')


def track_trial(trial: Trial):
    trial.update()
    trial.progress_turn = Response.count(trial) + 1


def track_players_around(player: Player, iteround: Round) -> bool:
    """Check if all players reached the round"""
    player.progress_round = iteround.id
    return all(p.field_maybe_none('progress_round') == iteround.id for p in player.group.get_players())


def track_players_atrial(player: Player, trial: Trial) -> bool:
    """Check if all players reached the trial"""
    player.progress_trial = trial.id
    return all(p.field_maybe_none('progress_trial') == trial.id for p in player.group.get_players())


def current(player: Player) -> Progress:
    """Get current round and trial (maybe none yet)"""
    group = player.group
    pagename = current_pagename(player.participant)
    iteround = Round.current(pagename, group=group)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def advance(curr: Progress) -> Progress:
    """Advance current round
    create/start/track round/trial
    """
    pagename, player, iteround, trial = curr
    group = player.group

    if iteround is None:
        iteround = Round.advance(pagename, group=group)
        trial = None

    if iteround.is_pristine and track_players_around(player, iteround):
        iteround.start()

    track_round(iteround)

    if iteround.progress_trials >= C.NUM_TRIALS:
        iteround.complete()
        set_payoffs(group, iteround)

    if iteround.is_closed:
        return Progress(pagename, player, iteround, None)

    if trial is None:
        trial = Trial.advance_next(iteround)

    if trial.is_pristine and track_players_atrial(player, trial):
        trial.start()
        track_trial(trial)

    return Progress(pagename, player, iteround, trial)


def advance_trial(curr: Progress):
    """Advance current trial
    Check completeness criteria, complete if needed
    """
    assert curr.is_valid
    pagename, player, iteround, trial = curr

    track_trial(trial)

    if trial.progress_turn > len(C.SEQUENCE):
        trial.complete()
        track_round(iteround)


def respond(curr: Progress, utterance: str, **kwargs) -> Response:
    assert curr.is_valid
    pagename, player, iteround, trial = curr

    assert player.role == curr.turn
    response = Response.create_next(trial, player, utterance=utterance, **kwargs)

    advance_trial(curr)
    return response
