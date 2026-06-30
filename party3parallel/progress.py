from typing import NamedTuple, Self, Type

from otree.api import Page

from .conf import C
from .models import Player, Group, Round, Trial, Response
from .models import set_payoff


class Progress(NamedTuple):
    """Holds all variables of progress and implements all progress methods"""

    player: Player  # it's a player-centric view of progress
    iteround: Round
    trial: Trial | None

    @classmethod
    def current(cls, page: Type[Page], player: Player) -> Self:
        """Get current round/trial for the page and player"""
        iteround = Round.pick_curr(page.__name__, group=player.group)  # might be not started
        assert iteround is not None, "Failed to pick next iteround"
        trial = Trial.current(iteround)  # might be None
        return cls(player, iteround, trial)

    @classmethod
    def track_round_completion(cls, iteround: Round) -> bool:
        """Check if the round should complete"""
        iteround.progress_trials = Trial.count(iteround, status="CLOSED")
        return iteround.progress_trials >= C.NUM_TRIALS

    @classmethod
    def track_trial_completion(cls, trial: Trial) -> bool:
        """Check if the trial should complete"""
        trial.progress_responses = Response.count(trial)
        return trial.progress_responses >= C.PLAYERS_PER_GROUP

    @classmethod
    def track_player_trial(cls, player: Player, trial: Trial):
        player.progress_trial = trial.id

    @classmethod
    def track_group_atrial(cls, group: Group, trial: Trial) -> bool:
        allgroup = [p for p in group.get_players() if p.participant.status != "dropout"]
        return all(p.field_maybe_none("progress_trial") == trial.id for p in allgroup)

    @classmethod
    def advance(cls, current: Self) -> Self:
        """Advance current progress"""

        player, iteround, trial = current

        cls.advance_round(player, iteround)
        trial = cls.iterate_trials(player, iteround, trial)
        return cls(player, iteround, trial)

    @classmethod
    def advance_round(cls, player: Player, iteround: Round):
        """start/stop current round"""

        if iteround.is_pristine:
            iteround.start()

        iteround.update()
        if iteround.is_running and cls.track_round_completion(iteround):
            iteround.complete()
            set_payoff(iteround)

    @classmethod
    def iterate_trials(cls, player: Player, iteround: Round, trial: Trial | None) -> Trial | None:
        """create/start current/next trial"""

        if iteround.is_closed:
            return None

        if trial is None:
            trial = Trial.pick_next(iteround)
        assert trial is not None, "Failed to pick next trial"

        cls.track_player_trial(player, trial)
        if trial.is_pristine and cls.track_group_atrial(iteround.group, trial):
            trial.start()

        return trial

    @classmethod
    def advance_trial(cls, player: Player, iteround: Round, trial: Trial, response: Response):
        """update/complete current trial"""

        trial.update()
        if cls.track_trial_completion(trial):
            trial.complete()
            cls.track_round_completion(iteround)

    @classmethod
    def respond(cls, current: Self, **kwargs) -> Response:
        """Respond to current trial"""

        player, iteround, trial = current
        assert trial is not None and trial.is_running, "Invalid responding"
        assert Response.count(trial, player=player) == 0, "Invalid extra response"

        response = Response.create_next(trial, player=player, **kwargs)
        response.evaluate()

        cls.advance_trial(player, iteround, trial, response)

        return response
