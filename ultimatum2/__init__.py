from .conf import C, config_condition  # noqa
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import custom_export_responses, custom_export_trials  # noqa
from .pages import page_sequence  # noqa


def creating_session(subsession: Subsession):
    session = subsession.session
    for group in subsession.get_groups():
        group.condition = config_condition(session)
