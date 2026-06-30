from .conf import C, config_condition  # noqa
from .models import Subsession, Group, Player  # noqa
from .models import custom_export_responses  # noqa
from .pages import page_sequence  # noqa


def creating_session(subsession: Subsession):
    session = subsession.session
    # per-group conditions
    for group in subsession.get_groups():
        group.condition = config_condition(session)


# def group_by_arrival_time_method(subsession: Subsession, waiting_players: list[Player]):
#     pass
