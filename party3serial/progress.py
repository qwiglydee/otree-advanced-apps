from typing import NamedTuple

from _extras.tracking import all_players_around, all_players_atrial, count_max_trials

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
        return self.player.group  # type: ignore

    @property
    def is_running(self) -> bool:
        return self.trial is not None and self.trial.is_running

    @property
    def turn(self) -> str | None:
        assert self.trial is not None
        if not self.trial.is_running:
            return None
        return C.SEQUENCE[self.trial.progress_turn - 1]


def current(page, player: Player) -> Progress:
    """Get current round and trial (maybe none yet)"""
    pagename = page.__name__
    iteround = Round.current(pagename, group=player.group)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def track_round(iteround: Round) -> bool:
    """Track round progress state and decide if to continue"""
    return count_max_trials(iteround, Trial, C.NUM_TRIALS)


def track_trial(trial: Trial) -> bool:
    """Track trial progress state and decide if to continue"""
    trial.progress_turn = Response.count(trial) + 1
    # continue until all responded or everyone agreed
    return trial.progress_turn <= C.CHAT_LEN and trial.agreed < C.PLAYERS_PER_GROUP


def advance(current: Progress) -> Progress:
    """Advance current round one iteration further"""
    pagename, player, iteround, trial = current
    assert trial is None or trial.is_closed, "Invalid advancing over incomplete trial"

    iteround = advance_round(current, iteround)

    if not iteround.is_closed:
        trial = advance_trial(current, iteround, trial)

    return Progress(pagename, player, iteround, trial)


def advance_round(current: Progress, iteround: Round | None) -> Round:

    if iteround is None:
        iteround = Round.pick(current.pagename, group=current.group)

    if iteround.is_pristine and all_players_around(current.player, iteround):
        iteround.start()

    iteround.update()

    if iteround.is_running and not track_round(iteround):
        iteround.complete()
        set_payoff(current.group, iteround)

    return iteround


def advance_trial(current: Progress, iteround: Round, trial: Trial | None) -> Trial:
    if trial is None:
        trial = Trial.pick_next(iteround)

    if trial.is_pristine and all_players_atrial(current.player, trial):
        trial.start()

    trial.update()

    if trial.is_running and not track_trial(trial):
        trial.complete()

    track_round(iteround)

    return trial


def respond(current: Progress, utterance: str, **kwargs) -> Response:
    pagename, player, iteround, trial = current
    assert iteround is not None and trial is not None, "Invalid responding to missing trial"
    assert player.role == current.turn

    response = Response.create_next(trial, player, utterance=utterance, **kwargs)

    advance_trial(current, iteround, trial)
    return response
