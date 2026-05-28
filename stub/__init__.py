from .conf import C, config_condition  # noqa
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import custom_export  # noqa
from .pages import page_sequence  # noqa


def creating_session(subsession: Subsession):
    session = subsession.session

    ## per-player conditions
    for player in subsession.get_players():
        player.condition = config_condition(session)

    ## per-group conditions
    # for group in subsession.get_groups():
    #     group.condition = config_condition(session)

    ## per-session condition
    # subsession.condition = config_condition(subsession.session)
