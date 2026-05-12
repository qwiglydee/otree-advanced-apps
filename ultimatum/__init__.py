from .conf import C, Points, config_condition  # noqa
from .models import Subsession, Group, Player, Round, Trial, Response  # noqa
from .models import custom_export_responses  # noqa
from .pages import page_sequence  # noqa


def creating_session(subsession: Subsession):
    session = subsession.session
    for group in subsession.get_groups():
        group.condition = config_condition(session)


def set_payoff(player: Player):
    iteround = Round.current('Main', group=player.group)
    player.payoff = iteround.total_scores[player.role]
