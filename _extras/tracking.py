from otree.api import BasePlayer

from _extras.itermodels import BaseRoundModel, BaseTrialModel


def all_players_around(player: BasePlayer, iteround: BaseRoundModel):
    """Check if all players in the group advanced to the same round"""
    current: int = iteround.id
    player.progress_round = current  # type: ignore
    others = [p for p in player.get_others_in_group() if p.participant.status != "dropout"]
    return all(p.field_maybe_none("progress_round") == current for p in others)


def all_players_atrial(player: BasePlayer, trial: BaseTrialModel):
    """Check if all players in the group advanced to the same trial"""
    current: int = trial.id
    player.progress_trial = current  # type: ignore
    others = [p for p in player.get_others_in_group() if p.participant.status != "dropout"]
    return all(p.field_maybe_none("progress_trial") == current for p in others)
