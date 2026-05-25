from otree.api import Page

from .models import Player


class Intro(Page):
    timeout_seconds = 30

    # this page contains hidden field filled by script
    form_model = "player"
    form_fields = ["age", "gender", "agreement", "hidden_localtime"]

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


class Slider(Page):
    page_styles = ["_extras/extra-fields.css"]
    page_scripts = ["_extras/extra-fields.js"]
    form_model = "player"
    form_fields = ["field_range"]


class RadioScale(Page):
    page_styles = ["_extras/extra-fields.css"]
    form_model = "player"
    form_fields = ["field_scale"]


class RadioGrid(Page):
    page_styles = ["_extras/extra-fields.css"]
    form_model = "player"
    form_fields = ["field_foo", "field_bar", "field_baz"]

    @staticmethod
    def vars_for_template(player: Player):
        return {
            "headers": [
                "Totally agree",
                "Somewhat agree",
                "Do not care",
                "Somewhat disagree",
                "Totally disagree",
            ]
        }


class Conditional(Page):
    page_styles = ["_extras/extra-fields.css"]
    form_model = "player"
    form_fields = ["field_qux", "field_qux_other"]


class Results(Page):
    pass


page_sequence = [
    Intro,
    Dropout,
    Misfit,
    Conditional,
    Slider,
    RadioScale,
    RadioGrid,
    Results,
]
