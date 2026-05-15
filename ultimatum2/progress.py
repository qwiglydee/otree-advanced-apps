from typing import NamedTuple


from .conf import C, Points
from .models import Player, Group, Round, Trial, Response
from .models import set_payoffs


class Progress(NamedTuple):
    pagename: str
    player: Player
    iteround: Round | None
    trial: Trial | None

    @property
    def group(self) -> Group:
        return self.iteround.group if self.iteround else None

    @property
    def is_valid(self) -> bool:
        return self.iteround and self.trial

    @property
    def is_running(self) -> bool:
        return self.trial and self.trial.is_running

    @property
    def stage(self):
        return self.trial.progress_stage if self.trial else None

    @property
    def turn(self) -> int:
        return C.STAGEROLES[self.trial.progress_stage] if self.is_running else None

    @property
    def dropout(self) -> bool:
        if not self.is_valid:
            return None
        return self.player.progress_dropout or self.group.progress_dropout


def current(page, player: Player) -> Progress:
    """Get current round and trial (maybe none yet)"""
    group = player.group
    pagename = page.__name__
    iteround = Round.current(pagename, group=group)
    trial = Trial.current(iteround) if iteround else None
    return Progress(pagename, player, iteround, trial)


def track_round(iteround: Round) -> bool:
    """Track round progress state and decide if to continue"""
    iteround.update()
    iteround.progress_trials = Trial.count(iteround, status='CLOSED')
    return iteround.progress_trials < C.NUM_TRIALS


def track_trial(trial: Trial) -> bool:
    """Track trial progress state and decide if to continue"""
    trial.update()
    if trial.proposal is None:
        trial.progress_stage = "PROPOSING"
    elif trial.decision is None:
        trial.progress_stage = "DECIDING"
    else:
        trial.progress_stage = None
    return trial.progress_stage is not None


def track_players_around(player: Player, iteround: Round) -> bool:
    """Track players to check they reached the round and indicate if to continue"""
    player.progress_round = iteround.id
    return all(p.field_maybe_none('progress_round') == iteround.id for p in player.group.get_players())


def track_players_atrial(player: Player, trial: Trial) -> bool:
    """Track players to check they reached the trial and indicate if to continue"""
    player.progress_trial = trial.id
    return all(p.field_maybe_none('progress_trial') == trial.id for p in player.group.get_players())


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

    if not track_round(iteround):
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


def advance_trial(curr: Progress):
    """Advance current trial
    Check completeness criteria, complete if needed
    """
    assert curr.is_valid
    pagename, player, iteround, trial = curr

    if not track_trial(trial):
        trial.complete()
        track_round(iteround)


def timeout(curr: Progress):
    """Handle timeout, reported from a waiting (live) player"""
    assert curr.is_valid
    pagename, player, iteround, trial = curr

    for other in player.get_others_in_group():
        other.progress_dropout = True

    iteround.close('TIMEOUTED')
    set_payoffs(iteround.group, iteround)
