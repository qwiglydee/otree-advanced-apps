from otree.views import Page

from .conf import C
from .models import Player, preassign_player


def get_template_rolename(page):
    # different page templates by players role: `Pagename_ROLE.html`
    pagename = page.__class__.__name__
    role = page.player.role
    return f"{__package__}/{pagename}_{role}.html"


def common_vars(player: Player):
    return {'condition': player.subsession.condition, 'endowment': C.ENDOWMENT[player.subsession.condition]}


class Intro(Page):
    timeout_seconds = 30
    form_model = "player"
    form_fields = ["age", "gender", "agreement"]

    vars_for_template = common_vars

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if timeout_happened:
            player.participant.status = 'dropout'

        if not player.dropout and not player.misfit:
            preassign_player(player)


class Instructions(Page):
    timeout_seconds = 30
    get_template_name = get_template_rolename
    vars_for_template = common_vars

    @staticmethod
    def is_displayed(player: Player):
        return not player.dropout and not player.misfit

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if timeout_happened:
            player.participant.status = 'dropout'


class Comprehension(Page):
    timeout_seconds = 30
    form_model = "player"
    form_fields = ["comprehended"]

    get_template_name = get_template_rolename
    vars_for_template = common_vars

    @staticmethod
    def is_displayed(player: Player):
        return not player.dropout and not player.misfit

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if timeout_happened:
            player.participant.status = 'dropout'


class Dropout(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.dropout or player.misfit or player.unqualified


page_sequence = [
    Intro,
    Instructions,
    Comprehension,
    Dropout,
]
