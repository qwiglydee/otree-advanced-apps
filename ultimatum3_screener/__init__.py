from .conf import C, config_condition  # noqa
from .models import Subsession, Group, Player  # noqa
from .pages import page_sequence  # noqa


def creating_session(subsession: Subsession):
    subsession.condition = config_condition(subsession.session)
