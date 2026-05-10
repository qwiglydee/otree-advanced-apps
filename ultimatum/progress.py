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


def max_trials(iteround: Round):
    return C.NUM_TRIALS


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
    player.progress_round = iteround.id
    players = player.group.get_players()
    return all(p.field_maybe_none('progress_round') == iteround.id for p in players)


def track_players_atrial(player: Player, trial: Trial) -> bool:
    player.progress_trial = trial.id
    players = player.group.get_players()
    return all(p.field_maybe_none('progress_trial') == trial.id for p in players)


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

    all_around = track_players_around(player, iteround)
    if iteround.is_pristine and all_around:
        iteround.start()

    track_round(iteround)

    if iteround.progress_trials >= max_trials(iteround):
        iteround.complete()

    if iteround.is_closed:
        return Progress(pagename, player, iteround, None)

    if trial is None:
        trial = Trial.advance_next(iteround)

    all_around = track_players_atrial(player, trial)
    if trial.is_pristine and all_around:
        trial.start()
        track_trial(trial)

    return Progress(pagename, player, iteround, trial)


def respond_proposal(current: Progress, proposal: Points, **kwargs) -> Response:
    pagename, player, iteround, trial = current
    assert current.is_valid
    assert trial.progress_stage == 'PROPOSING' and player.role == "P"

    response = Response.create_next(trial, player, stage='PROPOSING', p_proposal=proposal, **kwargs)
    track_trial(trial)

    return response


def respond_decision(current: Progress, decision: str, **kwargs) -> Response:
    pagename, player, iteround, trial = current
    assert current.is_valid
    assert trial.progress_stage == 'DECIDING' and player.role == "R"

    response = Response.create_next(trial, player, stage='DECIDING', r_decision=decision, **kwargs)
    track_trial(trial)

    trial.complete()
    track_round(iteround)

    return response
