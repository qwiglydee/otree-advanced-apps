from otree.api import Page

from .models import Player


class Intro(Page):
    timeout_seconds = 30

    # this page contains hidden field filled by script
    form_model = "player"
    form_fields = ["age", "gender", "localtime", "agreement"]

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        player.dropout = timeout_happened
        if not player.dropout:
            player.misfit = player.gender == "O"


class Dropout(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.dropout


class Misfit(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.misfit


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
    form_fields = [
        "q_baz",
        "q_baz_other",
        "q_qux",
        "q_qux_other",
    ]


class Results(Page):
    pass


page_sequence = [
    Intro,
    Dropout,
    Misfit,
    Questions1,
    Questions2,
    Questions3,
    Results,
]
