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


class Questions1scales(Page):
    form_model = "player"
    form_fields = ["q_range", "q_scale"]


class Questions2grid(Page):
    form_model = "player"
    form_fields = ["q_grid_foo", "q_grid_bar", "q_grid_baz"]


class Questions3other(Page):
    form_model = "player"
    form_fields = ["q_foo", "q_foo_other"]


class Results(Page):
    pass


page_sequence = [
    Intro,
    Dropout,
    Misfit,
    Questions1scales,
    Questions2grid,
    Questions3other,
    Results,
]
