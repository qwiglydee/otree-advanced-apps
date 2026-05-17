from typing import NamedTuple

from _stuff.tracking import track_players_all_around, track_players_all_atrial, track_round_trials

from .conf import C  # noqa
from .models import Player, Group, Round, Trial, Response
from .models import set_payoff


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
    def turn(self) -> str:
        assert self.is_running
        return self.trial.progress_turn


def current(page, player: Player) -> Progress:
    """Get current round and trial (maybe none yet)"""
    group = player.group
    pagename = page.__name__
    iteround = Round.current(pagename, group=group)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def track_round_continue(iteround: Round) -> bool:
    """Track round progress state and decide if to continue"""
    iteround.update()
    return track_round_trials(iteround, Trial, C.NUM_TRIALS)


def track_trial_continue(trial: Trial) -> bool:
    """Track trial progress state and decide if to continue"""
    trial.update()
    trial.progress_turn = Response.count(trial) + 1

    return trial.progress_turn <= C.PLAYERS_PER_GROUP


def advance(curr: Progress) -> Progress:
    """Advance current round one iteration further"""
    pagename, player, iteround, trial = curr
    assert trial is None or trial.is_closed, "Invalid advancing over incomplete trial"

    iteround = advance_round(player, pagename, iteround)

    if not iteround.is_closed:
        trial = advance_trial(player, iteround, trial)

    return Progress(pagename, player, iteround, trial)


def advance_round(player: Player, pagename: str, iteround: Round | None) -> Round:
    group: Group = player.group

    if iteround is None:
        iteround = Round.advance(pagename, group=group)

    if iteround.is_pristine and track_players_all_around(player, iteround):
        iteround.start()

    if iteround.is_running and not track_round_continue(iteround):
        iteround.complete()
        set_payoff(group, iteround)

    return iteround


def advance_trial(player: Player, iteround: Round, trial: Trial | None) -> Trial:
    if trial is None:
        trial = Trial.advance_next(iteround)

    if trial.is_pristine and track_players_all_atrial(player, trial):
        trial.start()

    if trial.is_running and not track_trial_continue(trial):
        trial.complete()

    track_round_continue(iteround)

    return trial


def respond(curr: Progress, utterance: str, **kwargs) -> Response:
    assert curr.is_running
    pagename, player, iteround, trial = curr

    assert player.id_in_group == curr.turn
    response = Response.create_next(trial, player, utterance=utterance, **kwargs)

    advance_trial(player, iteround, trial)
    return response
