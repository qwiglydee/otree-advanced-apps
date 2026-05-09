from otree.views import Page

from .conf import C, config_condition  # noqa
from .models import Subsession, Group, Player   # noqa

# SESSION


def creating_session(subsession: Subsession):
    session = subsession.session
    for player in subsession.get_players():
        player.condition = config_condition(session)


def set_payoff(player: Player):
    player.payoff = 0


# PAGES


class Intro(Page):
    # this page contains hidden field filled by script
    form_model = "player"
    form_fields = ["age", "gender", "localtime"]


class Questions1(Page):
    # this page contains radio scale
    template_name = f"{__package__}/Questions.html"
    page_styles = ["radio-scale.css"]
    form_model = "player"
    form_fields = ["q_range", "q_scale"]


class Questions2(Page):
    # the page uses condition-dependant field names
    template_name = f"{__package__}/Questions.html"
    form_model = "player"
    form_fields = ["q_foo_", "q_bar_"]

    def _get_form_fields(self):
        cond = self.player.condition.lower()
        return [f"{fld}{cond}" for fld in self.form_fields]


class Questions3(Page):
    # the page uses custom html an conditional fields
    page_scripts = ["otree-front-form.js"]
    form_model = "player"
    form_fields = ["q_baz", "q_baz_other", "q_qux", "q_qux_other", ]


class Results(Page):
    pass


page_sequence = [
    Intro,
    Questions1,
    Questions2,
    Questions3,
    Results,
]
