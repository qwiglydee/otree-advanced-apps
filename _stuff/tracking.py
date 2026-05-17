from otree.models import BasePlayer
from _stuff.itermodels import BaseRoundModel, BaseTrialModel


def track_players(player: BasePlayer, fieldname: str, value: any) -> bool:
    """Track players to check if they have the same value of a field
    return True if all players in group match
    """
    setattr(player, fieldname, value)
    others = [p for p in player.get_others_in_group() if p.participant.status != 'dropout']
    return all(p.field_maybe_none(fieldname) == value for p in others)


def track_players_all_around(player: BasePlayer, iteround: BaseRoundModel):
    """Check if all players in the group advanced to the same round"""
    return track_players(player, 'progress_round', iteround.id)


def track_players_all_atrial(player: BasePlayer, trial: BaseTrialModel):
    """Check if all players in the group advanced to the same trial"""
    return track_players(player, 'progress_trial', trial.id)


def track_round_trials(iteround: BaseRoundModel, TrialCls, max_trials: int):
    """Check if the round reached maximum trials"""
    count = TrialCls.count(iteround, status='CLOSED')
    iteround.progress_trials = count
    return count < max_trials
