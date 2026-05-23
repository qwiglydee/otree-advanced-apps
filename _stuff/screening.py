from otree.api import BasePlayer
from otree.database import AnyModel  # type: ignore
from otree.settings import PARTICIPANT_FIELDS

assert "assignment" in PARTICIPANT_FIELDS, "screening.py requires `assignment` participant field"


def copy_fields(src: AnyModel, dst: AnyModel, fieldnames: list[str]):
    """Copy fields between models (of different apps)"""
    for fld in fieldnames:
        setattr(dst, fld, getattr(src, fld))


def pre_assign_role(player: BasePlayer, role: str):
    """Assign a role in screener"""
    player.participant.assignment = role
    player._role = role  # type: ignore


def post_assign_role(player: BasePlayer):
    """Assign a role in main app"""
    player._role = player.participant.assignment  # type: ignore


def waiting_queues(waiting_players: list[BasePlayer], ROLES: list[str]):
    """Sort out waiting players by assigned roles"""
    return {role: [p for p in waiting_players if p.participant.assignment == role] for role in ROLES}
