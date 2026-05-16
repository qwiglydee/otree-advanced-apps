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
    form_model = "player"
    form_fields = ["age", "gender", "agreement"]

    vars_for_template = common_vars

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if not timeout_happened:
            preassign_player(player)


class Instructions(Page):
    get_template_name = get_template_rolename
    vars_for_template = common_vars


class Comprehension(Page):
    form_model = "player"
    form_fields = ["comprehended"]

    get_template_name = get_template_rolename
    vars_for_template = common_vars


page_sequence = [
    Intro,
    Instructions,
    Comprehension,
]
