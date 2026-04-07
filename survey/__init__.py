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
    form_model = "player"
    form_fields = ["age", "gender", "localtime"]

    @staticmethod
    def vars_for_template(player):  # pylint: disable=arguments-renamed
        # for debugging
        return {
            "condition": player.condition,
        }


class Questions1(Page):
    template_name = f"{__name__}/Questions.html"  # common template for form pages
    form_model = "player"
    form_fields = ["q_range", "q_scale"]


class Questions2(Page):
    """The page with dynamic field names
    The fields are suffixed with player condition
    """
    template_name = f"{__name__}/Questions.html"  # common template for form pages
    form_model = "player"
    form_fields = ["q_foo_", "q_bar_"]

    @staticmethod
    def get_form_fields(player: Player):
        cond = player.condition.lower()
        return [f"{fld}{cond}" for fld in Questions2.form_fields]


class Results(Page):
    pass


page_sequence = [
    Intro,
    Questions1,
    Questions2,
    Results,
]
