from .conf import C, Points, config_condition  # noqa
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import custom_export_responses, custom_export_trials  # noqa
from .pages import page_sequence  # noqa

from _stuff.screening import waiting_queues


def creating_session(subsession: Subsession):
    subsession.condition = config_condition(subsession.session)


def group_by_arrival_time_method(subsession: Subsession, waiting_players: list[Player]):
    queues = waiting_queues(waiting_players, C.ROLES)

    if any(len(q) == 0 for q in queues.values()):
        return None

    return [q.pop(0) for q in queues.values()]
