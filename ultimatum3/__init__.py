from .conf import C, config_condition  # noqa
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import custom_export_responses, custom_export_trials  # noqa
from .pages import page_sequence  # noqa

from _stuff.screening import waiting_queues


def creating_session(subsession: Subsession):
    subsession.condition = config_condition(subsession.session)


def group_by_arrival_time_method(subsession: Subsession, waiting_players: list[Player]):
    from ultimatum3_screener import Subsession as ScrSubsession

    scrsubsession = ScrSubsession.get_matching(subsession)

    queues = waiting_queues(waiting_players, C.ROLES)

    if all(len(q) > 0 for q in queues.values()):
        players = [q.pop(0) for q in queues.values()]
    else:
        players = None

    scrsubsession.track_queues(queues)

    return players
