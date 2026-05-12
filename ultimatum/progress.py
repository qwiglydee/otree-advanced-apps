from typing import NamedTuple

from _stuff.participant import current_pagename

from .conf import C, Points
from .models import Player, Round, Trial, Response


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
        return self.trial.progress_stage if self.trial else None

    @property
    def turn(self) -> int:
        return C.STAGEROLES[self.trial.progress_stage] if self.is_running else None


def track_round(iteround: Round):
    iteround.update()
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')


def track_trial(trial: Trial):
    trial.update()
    if trial.proposal is None:
        trial.progress_stage = "PROPOSING"
    elif trial.decision is None:
        trial.progress_stage = "DECIDING"
    else:
        trial.progress_stage = None


def track_players_around(player: Player, iteround: Round) -> bool:
    """Check if all players reached the round"""
    player.progress_round = iteround.id
    return all(p.field_maybe_none('progress_round') == iteround.id for p in player.group.get_players())


def track_players_atrial(player: Player, trial: Trial) -> bool:
    """Check if all players reached the trial"""
    player.progress_trial = trial.id
    return all(p.field_maybe_none('progress_trial') == trial.id for p in player.group.get_players())


def current(player: Player):
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

    if trial.progress_stage is None:
        trial.complete()
        track_round(iteround)


def respond_proposal(curr: Progress, proposal: Points, **kwargs) -> Response:
    assert curr.is_valid
    pagename, player, iteround, trial = curr
    assert player.role == curr.turn

    response = Response.create_next(trial, player, stage='PROPOSING', p_proposal=proposal, **kwargs)

    advance_trial(curr)
    return response


def respond_decision(curr: Progress, decision: str, **kwargs) -> Response:
    assert curr.is_valid
    pagename, player, iteround, trial = curr
    assert player.role == curr.turn

    response = Response.create_next(trial, player, stage='DECIDING', r_decision=decision, **kwargs)

    advance_trial(curr)
    return response
