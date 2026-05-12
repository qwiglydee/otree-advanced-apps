from .conf import C, config_condition, config_disclosure, config_layout  # noqa
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import custom_export_trials, custom_export_responses  # noqa
from .pages import page_sequence  # noqa


def creating_session(subsession: Subsession):
    session = subsession.session
    for player in subsession.get_players():
        player.condition = config_condition(session)
        player.disclosure = config_disclosure(session)
        player.layout = config_layout()
