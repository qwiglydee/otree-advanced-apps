from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.constants import BaseConstants

# from otree.currency import Currency as cu
# from otree.decimal import DecimalUnit
from otree import database as database

# from otree.database import ExtraModel
# from otree.read_csv import read_csv
from otree.forms import widgets
from otree.views import Page

from _stuff.config import get_session_param
from _stuff.widgets.hidden import HiddenWidget
from _stuff.widgets.slider import IntegerSlider


class C(BaseConstants):
    NAME_IN_URL = __name__
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ["C1", "C2"]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = database.StringField()

    age = database.IntegerField(min=18, max=90)
    gender = database.StringField(choices=[("M", "Male"), ("F", "Female"), ("O", "Other")])

    localtime = database.StringField(label="", blank=True, widget=HiddenWidget)

    q_range = database.IntegerField(
        label="How much do you something?",
        min=1, max=100,
        widget=IntegerSlider)

    q_scale = database.IntegerField(
        label="How much do you agree with something",
        choices=[
            (1, "1<br> totally disagree"),
            (2, "2<br> somewhat disagree"),
            (3, "3"),
            (4, "4<br> somewhat agree"),
            (5, "5<br> totally agree"),
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    q_foo_c1 = database.StringField(
        label="Something something?",
        choices=[
            ("F1", "Foo 1"),
            ("F3", "Foo 3"),
        ],
        widget=widgets.RadioSelect,
    )

    q_foo_c2 = database.StringField(
        label="Something something?",
        choices=[
            ("F2", "Foo 2"),
            ("F4", "Foo 4"),
        ],
        widget=widgets.RadioSelect,
    )

    q_bar_c1 = database.StringField(
        label="Something something?",
        choices=[
            ("B1", "Bar 1"),
            ("B3", "Bar 3"),
        ],
        widget=widgets.RadioSelect,
    )

    q_bar_c2 = database.StringField(
        label="Something something?",
        choices=[
            ("B2", "Bar 2"),
            ("B4", "Bar 4"),
        ],
        widget=widgets.RadioSelect,
    )

    q_baz = database.StringField(
        label="Something something?",
        choices=[
            ("Z1", "Baz 1"),
            ("Z2", "Baz 2"),
            ("Z3", "Baz 3"),
            ("Z4", "Baz 4"),
            ("Z0", "Other"),
        ],
    )

    q_baz_other = database.StringField(label="Specify baz", blank=True)

    q_qux = database.StringField(
        label="Something something?",
        choices=[
            ("Q1", "Qux 1"),
            ("Q2", "Qux 2"),
            ("Q3", "Qux 3"),
            ("Q4", "Qux 4"),
            ("Q0", "Other"),
        ],
    )

    q_qux_other = database.StringField(label="Specify qux", blank=True)

    def setup(self) -> None:
        """Configure some session-based fields and conditions"""
        self.condition = get_session_param(self.session, "condition", choices=C.CONDITIONS, default="random")


# SESSION


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        player.setup()


def set_payoff(player: Player):
    player.payoff = 0


# PAGES


class Intro(Page):
    page_styles = ["game-style.css"]
    # the localtimefield.js auto-fills hidden 'localtime' field
    page_scripts = ["localtimefield.js"]
    form_model = "player"
    form_fields = ["age", "gender", "localtime"]


class Questions1(Page):
    template_name = f"{__name__}/Questions.html"
    # the radio-scale.css applies to RadioSelectHorisontal
    page_styles = ["game-style.css", "radio-scale.css"]
    form_model = "player"
    form_fields = ["q_range", "q_scale"]


class Questions2(Page):
    template_name = f"{__name__}/Questions.html"
    page_styles = ["game-style.css"]
    form_model = "player"
    # Dynamic form_fields: names are prefixed with player condition
    form_fields = ["q_foo_", "q_bar_"]

    def _get_form_fields(self):
        cond = self.player.condition.lower()
        return [f"{fld}{cond}" for fld in self.form_fields]


class Questions3(Page):
    template_name = f"{__name__}/Fields.html"
    page_styles = ["game-style.css"]
    page_scripts = ["otree-front-inputs.js"]
    form_model = "player"
    form_fields = ["q_baz", "q_baz_other", "q_qux", "q_qux_other", ]


class Results(Page):
    page_styles = ["game-style.css"]


page_sequence = [
    Intro,
    Questions1,
    Questions2,
    Questions3,
    Results,
]
