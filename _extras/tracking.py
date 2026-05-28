from otree.api import BasePlayer

from _extras.itermodels import BaseRoundModel, BaseTrialModel


def track_players_all_around(player: BasePlayer, iteround: BaseRoundModel):
    """Check if all players in the group advanced to the same round"""
    current: int = iteround.id
    player.progress_round = current  # type: ignore
    others = [p for p in player.get_others_in_group() if p.participant.status != "dropout"]
    return all(p.field_maybe_none("progress_round") == current for p in others)


def track_players_all_atrial(player: BasePlayer, trial: BaseTrialModel):
    """Check if all players in the group advanced to the same trial"""
    current: int = trial.id
    player.progress_trial = current  # type: ignore
    others = [p for p in player.get_others_in_group() if p.participant.status != "dropout"]
    return all(p.field_maybe_none("progress_trial") == current for p in others)


def track_round_trials(iteround: BaseRoundModel, TrialCls, max_trials: int):
    """Check if the round reached maximum trials"""
    count: int = TrialCls.count(iteround, status="CLOSED")
    iteround.progress_trials = count  # type: ignore
    return count < max_trials


def track_trial_responses(trial: BaseTrialModel, ResponseCls, max_responses: int):
    """Check if the trial reached maximum responses"""
    count: int = ResponseCls.count(trial)
    trial.progress_responses = count  # type: ignore
    return count < max_responses
