from otree.api import BasePlayer
from .conf import C, config_condition  # noqa
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import custom_export_responses, custom_export_trials  # noqa
from .pages import page_sequence  # noqa

from _extras.screening import waiting_queues


def creating_session(subsession: Subsession):
    session = subsession.session
    subsession.condition = config_condition(session)


def group_by_arrival_time_method(subsession: Subsession, waiting_players: list[BasePlayer]):
    from ultimatum3_screener import Subsession as ScrSubsession

    scrsubsession = ScrSubsession.get_matching(subsession)

    roles = list(C.ROLES.values())
    queues = waiting_queues(waiting_players, roles)

    if all(len(q) > 0 for q in queues.values()):
        players = [q.pop(0) for q in queues.values()]
    else:
        players = None

    scrsubsession.track_queues(queues)

    return players
